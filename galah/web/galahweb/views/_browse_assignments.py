from galah.web.galahweb import app
from flask.ext.login import current_user
from galah.web.galahweb.auth import account_type_required
from galah.db.models import Class, Assignment
from galah.db.helpers.pretty import pretty_time_distance
from flask import render_template
import datetime

@app.route("/assignments")
@account_type_required("student")
def browse_assignments():
    # Grab all the current user's classes
    classes = Class.objects(id__in = current_user.classes).only("name")
        
    # Get all of the assignments in those classes
    assignments = list(Assignment.objects(
        for_class__in = current_user.classes
    ).only("name", "due", "for_class"))

    # Add a property to all the assignments so the template can display their
    # respective class easier. Additionally, add a plain text version of the
    # due date
    now = datetime.datetime.today()
    for i in assignments:
        try:
            i.class_name = next((j.name for j in classes if j.id == i.for_class))
        except StopIteration:
            app.logger.error("Assignment with id %s references non-existant "
                             "class with id %s." % (str(i.id, i.for_class)))
            
            i.class_name = "DNE"
            
        i.due_pretty = pretty_time_distance(now, i.due)
        
    return render_template("assignments.html", assignments = assignments)
