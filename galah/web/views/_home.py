# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import redirect, url_for, flash

@app.route("/home")
@app.route("/", methods = ["GET", "POST"])
def home():
    if not current_user.is_authenticated():
        return redirect(url_for("login"))

    return redirect(url_for("browse_assignments"))
