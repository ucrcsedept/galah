# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

## Create the form that takes simple archives ##
from flask.ext.wtf import Form
from wtforms.fields import FieldList, FileField, BooleanField
import wtforms.validators as validators

class SimpleArchiveForm(Form):
    archive = FieldList(FileField("Archive"), min_entries = 3)
    marked_as_final = BooleanField("Mark submission as final", default = False)

## The Actual View ##
from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, get_flashed_messages, request
from galah.db.models import Assignment, Submission, TestResult, User
from galah.base.pretty import pretty_time
from galah.web.util import create_time_element, GalahWebAdapter
import datetime
import logging

# Load Galah's configuration
from galah.base.config import load_config
config = load_config("web")

logger = GalahWebAdapter(logging.getLogger("galah.web.views.view_assignment"))

# Custom filter to output submission timestamp in ISO format
def isoformat(datetime):
    import re
    # Date String is close enough, just replace three trailing zeroes with Z
    datestring = datetime.isoformat()
    return re.sub(r"000$", "Z", datestring)

app.jinja_env.filters['isoformat'] = isoformat

@app.route("/assignments/<assignment_id>/")
@account_type_required(("student", "teacher", "teaching_assistant"))
def view_assignment(assignment_id):
    simple_archive_form = SimpleArchiveForm()

    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        logger.info("Invalid Assignment ID requested.")

        abort(404)

    # Retrieve the assignment
    try:
        assignment = Assignment.objects.get(id = id)
    except Assignment.DoesNotExist:
        logger.info("Non-extant ID requested.")

        abort(404)

    assignment.apply_personal_deadlines(current_user)

    # Get all of the submissions for this assignment
    submissions = list(
        Submission.objects(
            user = current_user.id,
            assignment = id
        ).order_by(
            "-most_recent",
            "-timestamp"
        )
    )

    # Get student submissions if being viewed as teacher
    student_submissions = []
    students = []
    if current_user.account_type in ["teacher", "teaching_assistant"]:
        students = list(
            User.objects(
                classes = assignment.for_class,
                account_type = "student"
            ).order_by(
                "-email"
            )
        )

        student_submissions = list(
            Submission.objects(
                user__in = [i.email for i in students],
                assignment = assignment_id,
                most_recent = True
            )
        )

    test_results = list(
        TestResult.objects(
            id__in = [i.test_results for i in submissions if i.test_results]
        )
    )

    # Match test results to submissions
    submissions_by_test_result = dict((i.test_results, i) for i in submissions)
    for i in test_results:
        submissions_by_test_result[i.id].test_results_obj = i

    # Current time to be compared to submission test_request_timestamp
    now = datetime.datetime.now()

    # Flag to set refresh trigger if user is waiting on test results
    wait_and_refresh = False

    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)
        i.status = "Submitted"

        # If the user submitted a test request and there aren't any results
        if (i.test_request_timestamp and not i.test_results):
            timedelta = now - i.test_request_timestamp
            i.show_resubmit = (timedelta > config["STUDENT_RETRY_INTERVAL"])
            if not i.show_resubmit:
                i.status = "Waiting for test results..."
            else:
                i.status = "Test request timed out"
        elif (i.test_results and i.test_results_obj.failed):
            i.status = "Tests Failed"
            i.show_resubmit = True
        elif (i.test_results and not i.test_results_obj.failed):
            i.status = "Tests Completed"

    wait_and_refresh = \
        any(i.status == "Waiting for test results..." for i in submissions)

    return render_template(
        "assignment.html",
        now = datetime.datetime.today(),
        create_time_element = create_time_element,
        assignment = assignment,
        submissions = submissions,
        simple_archive_form = simple_archive_form,
        wait_and_refresh = wait_and_refresh,
        new_submissions = [v for k, v in get_flashed_messages(with_categories = True) if k == "new_submission"],
        view_as_teacher = (current_user.account_type in ["teacher",
                                                         "teaching_assistant"]),
        students = students,
        student_submissions = student_submissions,
        markdown_enabled = config["MARKDOWN_ENABLED"],
        markdown_src = config["MARKDOWN_JS_SRC"],
        enumerate = enumerate
    )
