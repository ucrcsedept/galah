import pymongo, web, datetime, os, json, sys, os.path, zmq

urls = (
    "/?", "app.controllers.misc.Home",
    "/assignments/?", "app.controllers.browse.Assignments",
    "/assignments/([A-Fa-f0-9]{24})", "app.controllers.browse.Assignment",
    "/submit/([A-Fa-f0-9]{24})", "app.controllers.browse.SendSubmission",
    "/login", "app.controllers.account.Login",
    "/logout", "app.controllers.account.Logout",
    "/register/([A-Fa-f0-9]{24})", "app.controllers.account.Register"
)

# Have session cookies visible to client-side scripts
web.config.session_parameters["httponly"] = False

# Some of the imports may rely on this variable
app = web.application(urls, globals())

applicationRoot = os.path.abspath(__file__)

# Configurable Settings
viewDirectory = "app/views"
dbAddress = "localhost"
siteAddress = "localhost"

# Shepherd information
shepherdAddress = "localhost"
shepherdPort = 6668

# Bash script for git uploads via the web interface
pullScript = os.path.join(sys.path[0], "app/helpers/pull_script.sh")

# Connect to the database
db = pymongo.Connection(dbAddress).galah

# Create a monolithic zmq context
zmqContext = zmq.Context()

from app.helpers import utils, timeformat, auth

viewGlobals = {
    "utils": utils,
    "timeformat": timeformat,
    "datetime": datetime,
    "type": type,
    "unicode": unicode,
    "json": json,
    "auth": auth
}

# Set up the view renderers
view = web.template.render(viewDirectory, base = "base", globals = viewGlobals)
rawView = web.template.render(viewDirectory, globals = viewGlobals)
rawView.content_type = "text-html; charset=utf-8"
