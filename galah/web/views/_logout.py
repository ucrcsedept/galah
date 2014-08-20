from galah.web import app
from flask.ext.login import logout_user, current_user
from galah.web.auth import FlaskUser
from flask import redirect, url_for, flash
from galah.web.util import GalahWebAdapter
import logging

logger = GalahWebAdapter(logging.getLogger("galah.web.views.logout"))

@app.route("/logout")
def logout():
    if current_user.is_authenticated():
        # logout_user() cannot fail...
        logger.info("Succesfully logged out.")

        logout_user()
        
        flash("You have successfully logged out. You may now log in as another "
              "user or close this site.", category = "message")
    else:
        logger.info("User tried to log out when not logged in.")

        flash("You were not logged in and you are still not logged in.",
              category = "error")
    
    return redirect(url_for("login"))
