import pymongo, web, datetime, os, json

urls = (
    "/?", "app.controllers.misc.Home",
    "/assignments/?", "app.controllers.browse.Assignments",
    "/assignments/([A-Fa-f0-9]{24})", "app.controllers.browse.Assignment",
    "/login", "app.controllers.account.Login",
    "/logout", "app.controllers.account.Logout",
    "/register/([A-Fa-f0-9]{24})", "app.controllers.account.Register"
)

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

# Connect to the database
db = pymongo.Connection(dbAddress).galah

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
