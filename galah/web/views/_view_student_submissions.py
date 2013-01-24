# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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

logger = GalahWebAdapter(logging.getLogger(
        "galah.web.views.view_student_submissions"))

@app.route("/assignments/<assignment_id>/snapshot/<student_email>/")
@account_type_required(("teacher"))
def view_student_submissions(assignment_id, student_email):
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
        logger.info("Non-existent ID requested.")

        abort(404)

    # Make sure teacher is asking for information about a class they teach
    if assignment.for_class not in current_user.classes:
        logger.info("Attempt to view course information without permission.")
        
        abort(401)

    # Retrieve the student
    try:
        student = User.objects.get(email = student_email)
    except User.DoesNotExist:
        logger.info("Non-existent user ID required.")

    submissions = list(
        Submission.objects(
            user = student.id,
            assignment = id
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

    return render_template(
        "student_snapshot.html",
        now = datetime.datetime.today(),
        create_time_element = create_time_element,
        assignment = assignment,
        submissions = submissions,
        student = student
    )
