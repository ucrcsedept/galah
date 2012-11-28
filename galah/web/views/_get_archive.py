# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
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
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import (
    redirect, url_for, request, abort, current_app, send_file, Response
)
from galah.db.models import Archive
from bson.objectid import ObjectId, InvalidId

@app.route("/archives/<archive_id>")
def get_archive(archive_id):
    archive = None
    try:
        archive = Archive.objects.get(
            id = ObjectId(archive_id),
            archive_type = "assignment_package"
        )
    except InvalidId:
        abort(500)
    except Archive.DoesNotExist:
        pass

    # If we can't find the archive return a 404 error.
    if archive is None:
        abort(404)

    # Ensure that the requesting user has permission to view this archive
    if not current_user.is_authenticated() or \
            archive.requester != current_user.email:
        return current_app.login_manager.unauthorized()

    if archive.error_string:
        return Response(
            response = str(archive.error_string),
            headers = {
                "X-CallSuccess": "False",
            },
            mimetype = "text/plain"
        )
    else:
        return send_file(archive.file_location)