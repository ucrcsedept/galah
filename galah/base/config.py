# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
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

import datetime

# Default configuration values for Galah.
defaults = {
    "global/CURRENT_VERSION": "v0.1.3",
    "global/SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "global/MONGODB": "galah",
    "global/SISYPHUS_ADDRESS": "ipc:///tmp/sisyphus.sock",
    "web/DEBUG": True,
    "web/SECRET_KEY": "Very Secure Key",
    "web/HOST_URL": "http://localhost:5000",
    "web/STUDENT_ARCHIVE_LIFETIME": datetime.timedelta(minutes = 2),
    "web/SOURCE_HOST": "https://github.com/brownhead/galah",
    "sisyphus/TEACHER_ARCHIVE_LIFETIME": datetime.timedelta(minutes = 2)
}

import imp
import logging
import os
from galah.base.utility import tuplify

loaded = None
def load_config(domain):
    """
    Parses and loads up the Galah configuration file and extracts the
    configuration data for the given domain (ex: "web" or "sheep").

    Global configuration options will always be returned, no matter the domain.

    The configuration file will only be loaded once per instance of the
    interpreter, so feel free to call this function multiple times in many files
    to avoid ugly dependency issues.

    """

    global loaded

    # Note whether this is the first time we're processing the configuraiton. If
    # it is, we'll want to attach the global log handlers.
    first_load = loaded is None

    # Load the configuration if it hasn't been loaded yet. Note this ensures
    # that the configuration is only loaded once per instance of the
    # interpreter
    if not loaded:
        if os.path.isfile("/etc/galah/galah.config"):
            loaded = imp.load_source(
                "user_config_file", "/etc/galah/galah.config"
            )

    local_config = {}

    # Note we make a **shallow** copy of the defaults here
    user_config = dict(defaults)

    # If the configuration didn't load correctly, just use the defaults
    if loaded:
        user_config.update(loaded.config)

    # The prefix values we will look for when scanning the configuration file.
    prefix = "%s/" % domain
    global_prefix = "global/"

    # Grab all the configuration values for the given domain, and any global
    # configuration values.
    for k, v in user_config.items():
        if k.startswith(prefix) and k != len(prefix):
            local_key = k[len(prefix):]

            local_config[local_key] = v
        elif k.startswith(global_prefix) and k != len(global_prefix):
            global_key = k[len(global_prefix):]

            local_config[global_key] = v

    return local_config
