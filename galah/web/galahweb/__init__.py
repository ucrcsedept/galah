from flask import Flask
app = Flask("galah.web.galahweb")

if not app.debug:
    if not app.config.from_envvar("GALAH_WEB_CONFIG", silent = True):
        try:
            app.config.from_pyfile("/etc/galah/web.config")
        except IOError:
            exit(
                "Environmental variable GALAH_WEB_CONFIG not set to valid file "
                "path and /etc/galah/web.config was not found. Either point "
                "GALAH_WEB_CONFIG at a valid config file or place your config "
                "file at /etc/galah/web.config."
            )
            
            

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

import views
