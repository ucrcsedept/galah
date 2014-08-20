# The actual view
from galah.web import app
from flask import render_template, url_for
from werkzeug.exceptions import InternalServerError, NotFound

from galah.web.util import GalahWebAdapter
import logging
logger = GalahWebAdapter(logging.getLogger("galah.web.views.error"))

from galah.base.config import load_config
config = load_config("web")

@app.errorhandler(404)
def notfound(e):
    logger.info("User accessed unavailable page.")

    return render_template("notfound.html"), 404

@app.errorhandler(500)
def error(e):
    # Log the error if it's not a 404 or purposeful abort(500).
    if type(e) is not InternalServerError and type(e) is not NotFound:
        logger.exception("An error occurred while rendering a view.")

    return render_template(
        "error.html",
        report_to = config["REPORT_ERRORS_TO"]
    ), 500

@app.errorhandler(413)
def toobig(e):
	logger.info("User tried to upload a file that was too large.")

	return render_template("toobig.html"), 413
