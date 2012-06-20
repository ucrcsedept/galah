from galahweb import app
from flask.ext.login import current_user
from galahweb.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template
from galah.db.models import Assignment, Submission
from galah.db.helpers.pretty import pretty_time

@app.route("/assignments/<assignment_id>")
@account_type_required("student")
def view_assignment(assignment_id):
    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        app.logger.debug("Invalid ID")
        
        abort(404)
    
    # Retrieve the assignment
    # TODO: Add error handling here.. Not sure what exception it throws, trying
    # it out made me think there are errors in mongoengine as I got an
    # AttributeError
    assignment = Assignment.objects.get(id = id)
    
    # Get all of the submissions for this assignmnet
    submissions = list(Submission.objects(user = current_user.id, assignment = id))
    
    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)
    
    return render_template("assignment.html", assignment = assignment, submissions = submissions)
