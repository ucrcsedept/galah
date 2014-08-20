from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import (
    redirect, url_for, request, abort, current_app, send_file, Response
)
from galah.db.models import CSV
from bson.objectid import ObjectId, InvalidId
from galah.web.util import GalahWebAdapter
import logging

logger = GalahWebAdapter(logging.getLogger("galah.web.views.get_csv"))

@app.route("/reports/csv/<csv_id>")
def get_csv(csv_id):
    csv = None
    print csv_id
    try:
        print ObjectId(csv_id)
        csv = CSV.objects.get(id = ObjectId(csv_id))
        print csv
    except InvalidId:
        logger.info("Invalid ID requested.")

        abort(500)
    except CSV.DoesNotExist:
        pass

    # If we can't find the CSV file return a 404 error.
    if csv is None:
        logger.info("Could not find CSV file with given ID.")

        abort(404)

    # Ensure that the requesting user has permission to view this csv
    if not current_user.is_authenticated() or \
            csv.requester != current_user.email:
        logger.info(
            "User requested csv they do not have permission to view."
        )

        return current_app.login_manager.unauthorized()

    if csv.error_string:
        logger.info(
            "User requested csv that had an error during creation: %s.",
            csv.error_string
        )

        return Response(
            response = "Internal server error.",
            headers = {
                "X-CallSuccess": "False",
            },
            mimetype = "text/plain"
        )
    else:
        return send_file(csv.file_location)
