import datetime

# Default configuration values for Galah.
defaults = {
    "global/CURRENT_VERSION": "v0.1.3",
    "global/SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "global/CSV_DIRECTORY": "/var/local/galah/reports/csv/",
    "global/HARNESS_DIRECTORY": "/var/local/galah/web/harness/",
    "global/MONGODB": "galah",
    "global/SISYPHUS_ADDRESS": "ipc:///tmp/sisyphus.sock",
    "global/EMAIL_VALIDATION_REGEX":
        "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
    "web/ALIAS": "Galah",
    "web/DEBUG": True,
    "web/SECRET_KEY": "Very Secure Key",
    "web/HOST_URL": "http://localhost:5000",
    "web/STUDENT_ARCHIVE_LIFETIME": datetime.timedelta(minutes = 2),
    "web/STUDENT_RETRY_INTERVAL": datetime.timedelta(minutes = 3),
    "web/SOURCE_HOST": "https://github.com/galah-group/galah",
    "web/REPORT_ERRORS_TO": None,
    "web/MAX_CONTENT_LENGTH": None,
    "web/GOOGLE_LOGIN_HEADING":
        "If you have a Google account, please log in with it by clicking the "
        "the button below.",
    "web/GOOGLE_LOGIN_CAPTION": "Login with Google",
    "sisyphus/TEACHER_ARCHIVE_LIFETIME": datetime.timedelta(minutes = 2),
    "sisyphus/TEACHER_CSV_LIFETIME": datetime.timedelta(minutes = 2),
    "sheep/NCONSUMERS": 1,
    "sheep/VIRTUAL_SUITE": "dummy",
    "sheep/vz/OS_TEMPLATE": "centos-6-x86_64",
    "sheep/vz/MAX_MACHINES": 2,
    "sheep/vz/LOW_MACHINE_THRESHOLD": 1,
    "sheep/vz/LOW_MACHINE_PERIOD": datetime.timedelta(minutes = 1),
    "sheep/vz/VZCTL_RETRY_TIMEOUT": datetime.timedelta(seconds = 30),
    "sheep/vz/CALL_MKDIR": True,
    "sheep/vz/VM_TESTABLES_DIRECTORY": "/tmp/testables/",
    "sheep/vz/VM_HARNESS_DIRECTORY": "/tmp/harness/",
    "sheep/vz/BOOTSTRAPPER": "/vagrant/galah/galah/sheep/virtualsuites/vz/bootstrapper.py",
    "sheep/vz/TESTUSER_UID": 1000,
    "sheep/vz/TESTUSER_GID": 1000,
    "sheep/vz/VM_SUBNET": "10.0.1",
    "sheep/vz/VM_PORT": 6668, # Must be changed in the bootstrapper as well.
    "shepherd/SHEEP_SOCKET": "ipc:///tmp/shepherd-sheep.sock",
    "shepherd/PUBLIC_SOCKET": "ipc:///tmp/shepherd-public.sock",
    "shepherd/REQUEST_QUEUE_TIMEOUT": datetime.timedelta(minutes = 1),
    "shepherd/SERVICE_TIMEOUT": datetime.timedelta(minutes = 1),
    "shepherd/BLEET_TIMEOUT":  datetime.timedelta(seconds = 30)
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
    config_file = os.environ.get("GALAH_CONFIG_PATH",
                                 "/etc/galah/galah.config")
    if not loaded:
        if os.path.isfile(config_file):
            loaded = imp.load_source(
                "user_config_file", config_file
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
    # configuration values, then place the rest of the configuration values
    # in there as well.
    for k, v in user_config.items():
        if k.startswith(prefix) and len(k) != len(prefix):
            local_key = k[len(prefix):]

            local_config[local_key] = v
        elif k.startswith(global_prefix) and len(k) != len(global_prefix):
            global_key = k[len(global_prefix):]

            local_config[global_key] = v
        elif "/" in k:
            local_config[k] = v

    return local_config
