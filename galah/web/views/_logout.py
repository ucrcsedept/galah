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
