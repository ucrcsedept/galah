from galah.web.galahweb import app
from flask.ext.login import current_user
from galah.web.galahweb.auth import FlaskUser
from flask import redirect, url_for, flash

@app.route("/home")
def home():
    if not current_user.is_authenticated():
        return redirect(url_for("login"))
    
    return redirect(url_for("browse_assignments"))
