# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import (
    redirect, url_for, request, abort, current_app, send_file, Response
)
from galah.db.models import Archive
from bson.objectid import ObjectId, InvalidId
from galah.web.util import GalahWebAdapter
import logging

logger = GalahWebAdapter(logging.getLogger("galah.web.views.get_archive"))

@app.route("/archives/<archive_id>")
def get_archive(archive_id):
    archive = None
    try:
        archive = Archive.objects.get(
            id = ObjectId(archive_id),
            archive_type = "assignment_package"
        )
    except InvalidId:
        logger.info("Invalid ID requested.")

        abort(500)
    except Archive.DoesNotExist:
        pass

    # If we can't find the archive return a 404 error.
    if archive is None:
        logger.info("Could not find archive with given ID.")

        abort(404)

    # Ensure that the requesting user has permission to view this archive
    if not current_user.is_authenticated() or \
            archive.requester != current_user.email:
        logger.info(
            "User requested archive they do not have permission to view."
        )

        return current_app.login_manager.unauthorized()

    if archive.error_string:
        logger.info(
            "User requested archive that had an error during creation: %s.",
            archive.error_string
        )

        return Response(
            response = "Internal server error.",
            headers = {
                "X-CallSuccess": "False",
            },
            mimetype = "text/plain"
        )
    else:
        return send_file(archive.file_location)
