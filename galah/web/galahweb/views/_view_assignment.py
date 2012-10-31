## Create the form that takes simple archives ##
from flask.ext.wtf import Form, FileField, validators, BooleanField

class SimpleArchiveForm(Form):
    archive = FileField("Archive", [validators.Required()])
    
## The Actual View ##
from galah.web.galahweb import app
from flask.ext.login import current_user
from galah.web.galahweb.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, get_flashed_messages
from galah.db.models import Assignment, Submission
from galah.db.helpers.pretty import pretty_time, pretty_time_distance
import datetime

@app.route("/assignments/<assignment_id>/")
@account_type_required("student")
def view_assignment(assignment_id):
    simple_archive_form = SimpleArchiveForm()
    
    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        app.logger.debug("Invalid ID (%s)" % str(id))
        
        abort(404)
    
    # Retrieve the assignment
    try:
        assignment = Assignment.objects.get(id = id)
    except Assignment.DoesNotExist:
        app.logger.debug("Non-extant ID (%s)" % str(id))
        
        abort(404)
    
    # Get all of the submissions for this assignmnet
    submissions = list(Submission.objects(user = current_user.id, assignment = id))
    
    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)
    
    # Figure out if submissions should be allowed
    cutoff_time = None
    if assignment.due_cutoff and \
            assignment.due_cutoff < datetime.datetime.today():
        cutoff_time = pretty_time_distance(
            datetime.datetime.today(), assignment.due_cutoff
        )
    
    return render_template(
        "assignment.html",
        cutoff_time = cutoff_time,
        assignment = assignment, 
        submissions = submissions,
        simple_archive_form = simple_archive_form,
        new_submissions = [v for k, v in get_flashed_messages(with_categories = True) if k == "new_submission"]
    )
