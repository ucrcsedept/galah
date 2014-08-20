from flask import Flask
from flask.ext.markdown import Markdown
app = Flask("galah.web")
Markdown(app)

# Hack to work around the destruction of error handlers by Flask's deferred
# processing.
app.logger_name = "nowhere"
app.logger

from galah.base.config import load_config
app.config.update(load_config("web"))

oauth_enabled = bool(
    app.config.get("GOOGLE_SERVERSIDE_ID") and
    app.config.get("GOOGLE_SERVERSIDE_SECRET") and
    app.config.get("GOOGLE_APICLIENT_ID") and
    app.config.get("GOOGLE_APICLIENT_SECRET")
)

import mongoengine
mongoengine.connect(app.config["MONGODB"])

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

import views
