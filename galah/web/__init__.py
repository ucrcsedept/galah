# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from flask import Flask
app = Flask("galah.web")

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

cas_enabled = bool(
    app.config.get("CAS_SERVER_URL")
)

import mongoengine
mongoengine.connect(app.config["MONGODB"])

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

# Enable profiling
if app.config["PROFILING_ENABLED"]:
    import cProfile
    pr = cProfile.Profile()
    pr.enable()

    import datetime
    import tempfile
    import os
    @app.before_request
    def dump_profile_data():
        if datetime.datetime.today() - dump_profile_data.last_dump > \
                app.config["PROFILING_DUMP_INTERVAL"]:
            pr.dump_stats(dump_profile_data.dump_filepath)
            dump_profile_data.last_dump = datetime.datetime.today()
    dump_profile_data.last_dump = datetime.datetime.today()
    file_descriptor, dump_profile_data.dump_filepath = tempfile.mkstemp(
        prefix = "cprof",
        dir = app.config["PROFILING_DUMP_DIRECTORY"]
    )
    os.close(file_descriptor)

import views
