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
from flask import abort, render_template, request, flash, redirect, jsonify, \
                  url_for
from galah.db.models import Submission, Assignment
from galah.base.pretty import pretty_list, plural_if
from galah.web.util import is_url_on_site, GalahWebAdapter
from werkzeug import secure_filename
import os.path
import subprocess
import datetime
import shutil
import tempfile
import datetime
import logging

from _view_assignment import SimpleArchiveForm

logger = \
    GalahWebAdapter(logging.getLogger("galah.web.views.upload_submissions"))

@app.route("/assignments/<assignment_id>/upload", methods = ["POST"])
@account_type_required(("student", "teacher"))
def upload_submission(assignment_id):
    # Figure out which assignment the user asked for.
    try:
        id = ObjectId(assignment_id)
        assignment = Assignment.objects.get(id = id)
    except (InvalidId, Assignment.DoesNotExist) as e:
        logger.info("Could not retrieve assignment: %s", str(e))
        
        abort(404)
    
    # Figure out where we should redirect the user to once we're done.
    redirect_to = request.args.get("next") or request.referrer

    if not is_url_on_site(app, redirect_to):
        # Default going back to the assignment screen
        redirect_to = url_for(
            "view_assignment",
            assignment_id = assignment_id
        )
    
    # Check if the assignment's cutoff date has passed
    if assignment.due_cutoff and \
            assignment.due_cutoff < datetime.datetime.today():
        logger.info("Submission rejected, cutoff date has already passed.")

        return craft_response(
            error = "The cutoff date has already passed, your submission was "
                    "not accepted."
        )

    form = SimpleArchiveForm()
    if not form.validate_on_submit():
        logger.info("Submission rejected. Validation failure.")

        flash("The files you passed in were invalid.", category = "error")

        return redirect(redirect_to)

    if not [i for i in form.archive.entries if i.data.filename]:
        logger.info("Submission rejected. User did not submit any files.")

        flash("You did not submit any files.", category = "error")

        return redirect(redirect_to)

    new_submission = Submission(
        assignment = id,
        user = current_user.id,
        timestamp = datetime.datetime.now(),
        marked_for_grading = True,
        most_recent = True
    )
    new_submission.id = ObjectId()

    # Craft a unique directory path where we will store the new submission. We
    # are guarenteed an ObjectId is unique. However we are not guarenteed that
    # we will have the proper permissions and that we will be able to make the
    # directory thus this could error because of that.
    new_submission.testables = new_submission.getFilePath()
    os.makedirs(new_submission.testables)

    # Save each file the user uploaded into the submissions directory
    for i in form.archive.entries:
        if not i.data.filename:
            continue

        # Figure out where we want to save the user's file
        file_path = os.path.join(
            new_submission.testables, secure_filename(i.data.filename)
        )

        # Do the actual saving
        i.data.save(file_path)
    
    new_submission.uploaded_filenames.extend(
        secure_filename(i.data.filename) for i in form.archive.entries
            if i.data.filename
    )

    logger.info(
        "Succesfully uploaded a new submission (id = %s) with files %s.",
        str(new_submission.id),
        str(new_submission.uploaded_filenames)
    )

    # The old "most_recent" submission is no longer the most recent.
    Submission.objects(
        user = current_user.email, 
        assignment = id, 
        most_recent = True
    ).update(
        multi = False,
        unset__most_recent = 1
    )

    new_submission.save()
    
    # Communicate to the next page what submission was just added.
    flash(new_submission.id, category = "new_submission")

    flash(
        "Successfully uploaded %s %s." %
            (
                plural_if("file", len(new_submission.uploaded_filenames)),
                pretty_list(new_submission.uploaded_filenames)
            ),
        category = "message"
    )
    
    # Everything seems to have gone well
    return redirect(redirect_to)
