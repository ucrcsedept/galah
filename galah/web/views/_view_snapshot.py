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

logger = GalahWebAdapter(logging.getLogger("galah.web.views.view_snapshot"))

# Custom filter to output submission timestamp in ISO format
def isoformat(datetime):
    import re
    # Date String is close enough, just replace three trailing zeroes with Z
    datestring = datetime.isoformat()
    return re.sub(r"000$", "Z", datestring)

app.jinja_env.filters['isoformat'] = isoformat

@app.route("/assignments/<assignment_id>/snapshot/<student_email>")
@account_type_required(("teacher", "teaching_assistant"))
def view_snapshot(assignment_id, student_email):
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
        deadline = current_user.personal_deadline
        if str(assignment_id) in deadline:
            assignment.due_cutoff = deadline[str(assignment_id)]
    except Assignment.DoesNotExist:
        logger.info("Non-extant ID requested.")

        abort(404)

    # Retrieve the student
    try:
        student = User.objects.get(email = student_email)
    except User.DoesNotExist:
        logger.info("Non-extant Student ID requested.")

    # Get all of the submissions for this assignment
    submissions = list(
        Submission.objects(
            user = student.id,
            assignment = id
        ).order_by(
            "-most_recent",
            "-timestamp"
        )
    )

    test_results = list(
        TestResult.objects(
            id__in = [i.test_results for i in submissions if i.test_results]
        )
    )

    # Match test results to submissions
    for i in submissions:
        for j in test_results:
            if i.test_results == j.id:
                i.test_results_obj = j

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
        view_snapshot = True,
        student = student,
        enumerate = enumerate
    )
