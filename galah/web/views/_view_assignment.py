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

## Create the form that takes simple archives ##
from flask.ext.wtf import Form, FieldList, FileField, validators, BooleanField

class SimpleArchiveForm(Form):
    archive = FieldList(FileField("Archive"), min_entries = 3)
    
## The Actual View ##
from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, get_flashed_messages
from galah.db.models import Assignment, Submission
from galah.base.pretty import pretty_time
from galah.web.util import create_time_element, GalahWebAdapter
import datetime
import logging

logger = GalahWebAdapter(logging.getLogger("galah.web.views.view_assignment"))

@app.route("/assignments/<assignment_id>/")
@account_type_required(("student", "teacher"))
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

    # Get all of the submissions for this assignmnet
    submissions = list(
        Submission.objects(
            user = current_user.id,
            assignment = id
        ).order_by(
            "-most_recent",
            "-timestamp"
        )
    )
    
    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)
    
    return render_template(
        "assignment.html",
        now = datetime.datetime.today(),
        create_time_element = create_time_element,
        assignment = assignment, 
        submissions = submissions,
        simple_archive_form = simple_archive_form,
        new_submissions = [v for k, v in get_flashed_messages(with_categories = True) if k == "new_submission"]
    )
