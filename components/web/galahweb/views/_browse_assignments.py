from galahweb import app
from flask.ext.login import login_required
from galahweb.auth import account_type_required

@app.route("/assignments")
@account_type_required("student")
def browse_assignments():
    # Grab all the current user's classes
    classes = Class.objects(id__in = current_user.classes).only("name")
        
    # Get all of the assignments in those classes
    assignments = list(models.Assignment.objects(for_class__in = user.classes))
