#!/usr/bin/env python

# The default configuration settings
config = {
    "api_url": "http://localhost:5000/api/call",
    "login_url": "http://localhost:5000/api/login"
}

import json
def _to_json(obj):
    """
    Serializes an object into a JSON representation. The returned string will be
    compressed appropriately for network transfer.
    
    """
    
    return json.dumps(obj, separators = (",", ":"))

def _form_call(api_name, *args, **kwargs):
    """
    Creates a tuple or dict (depending on the existence of keyword arguments)
    that can be serialized to JSON and sent to galah.api.
    
    """
    
    if not kwargs:
        return (api_name, ) + args
    else:
        # kwargs is basically already what we want, we just need to add the
        # positional arguments and name of the API call.
        kwargs.update({"api_name": api_name, "args": args})
        
        return kwargs

from warnings import warn
import requests

# We'll need to store any cookies the server gives us (mainly the auth cookie)
# and requests' sessions give us a nice way to do that.
_session = requests.session()

def login(email, password):
    request = _session.post(
        config["login_url"], data = {"email": email, "password": password}
    )
    
    request.raise_for_status()
    
    # Check if we successfully logged in.
    if request.headers["X-CallSuccess"] != "True":
        raise RuntimeError(request.text)
    
    # Nothing bad happened, go ahead and return what the server sent back
    return request.text

def call(api_name, *args, **kwargs):
    """
    Makes an API call to the server with the given arguments. This function will
    block until the server sends its response.
    
    """
    
    # May throw a requests.ConnectionError here if galah.api is unavailable.
    request = _session.post(
        config["api_url"],
        data = _to_json(_form_call(api_name, *args, **kwargs)),
        headers = {"Content-Type": "application/json"}
    )
    
    # Will throw a requests.URLError or requests.HTTPError here if either
    # occurred.
    request.raise_for_status()
    
    # Currently only textual data is ever returned but other types of data may
    # be returned in the future. If this warning goes off that means that this
    # script needs to be updated to a new version.
    if not request.headers["Content-Type"].startswith("text/plain"):
        warn(
            "Expecting text/plain content, got %s. You may need to update this "
            "program." % request.headers["Content-Type"].split(";")[0]
        )
    
    # Check if the server encountered an error processing the request.
    # Unfortunately the status code can't be set to 500 on the server side
    # because of some issues with Flask, so we have this custom header.
    if request.headers["X-CallSuccess"] != "True":
        raise RuntimeError(request.text)
    
    # Nothing bad happened, go ahead and return what the server sent back
    return request.text

import sys
from optparse import OptionParser, make_option
def parse_arguments(args = sys.argv[1:]):
    option_list = [
        make_option(
            "--user", "-u", metavar = "USERNAME",
            help = "The username to authenticate with. The password should be "
                   "available in the evironmental variable GALAH_PASSWORD "
                   "if this option is used."
        ),
        make_option(
            "--config", "-c", metavar = "FILE",
            help = "The configuration file to use. By default "
                   "~/.galah/config/api_client.config is used if available."
        ),
        make_option(
            "--shell", "-s", action = "store_true",
            help = "If specified, you will be placed in an interactive "
                   "bash shell that will allow you to execute api commands as "
                   "if they were regular system commands."
        )
    ]

    parser = OptionParser(
        description = "Command line interface to Galah for use by instructors "
                      "and administrators.",
        option_list = option_list,
        epilog = "Example usage in bash: GALAH_PASSWORD=test python "
                 "api_client.py -u john@doe.com get_submissions "
                 "SOME0ASSIGNMENT0ID"
    )

    options, args = parser.parse_args(args)

    if not options.shell and len(args) == 0:
        parser.error("At least one argument must be supplied.")

    return (options, args)

def parse_configuration(config_file):
    import json

    config = json.load(config_file)

    return config

def exec_to_shell():
    # The name of the currently execute script (ex: api_client.py)
    script_location, script_name = os.path.split(__file__)
    script_location = os.path.abspath(script_location)

    # Retrieve all of the available commands from the server
    api_info = json.loads(call("get_api_info"))
    commands = [i["name"] for i in api_info]

    rcfile_path = os.path.join(os.environ["HOME"], ".galah/tmp/shellrc")

    rcfile = None
    if "HOME" in os.environ:
        try:
            os.makedirs(os.path.dirname(rcfile_path))
        except OSError:
            pass

        try:
            rcfile = open(rcfile_path, "w")
        except IOError:
            pass

    if rcfile == None:
        rcfile, rcfile_path = tempfile.mkstemp()

        print rcfile_path
        sys.stdout.flush()

    print >> rcfile, "PATH=%s:$PATH" % script_location

    for i in commands:
        print >> rcfile, 'alias %s="%s %s"' % (i, script_name, i)

    # Manually ensure that there's nothing buffered as no cleanup will occur
    # when we exec below.
    rcfile.flush()

    os.execlp("bash", "bash", "--rcfile", rcfile_path)

import os
if __name__ == "__main__":
    options, args = parse_arguments()

    if options.shell:
        exec_to_shell()

    if options.config:
        try:
            config_file = open(options.config)

            config.update(parse_configuration(config_file))
        except IOError:
            exit("File '%s' could not be opened for reading." % config_file)
    else:
        try:
            config_file = open(os.path.join(
                os.environ["HOME"], ".galah/config/api_client.config"
            ))

            config.update(parse_configuration(config_file))
        except (IOError, KeyError):
            pass

    user = options.user or config.get("user")
    password = os.environ.get("GALAH_PASSWORD") or config.get("password")

    if user and not password:
        exit(
            "Username specified but no password given (did you forget to set "
            "GALAH_PASSWORD?)."
        )

    if user and password:
        try:
            login(user, password)

            print "--Logged in as %s--" % user
        except requests.exceptions.ConnectionError as e:
            print >> sys.stderr, "Could not connect with the given url '%s':" \
                    % config["login_url"]
            print >> sys.stderr, "\t" + str(e)

            exit(1)
        except RuntimeError:
            print >> sys.stderr, "Could not log in with provided user name " \
                  "and password. (Did you remember to set GALAH_PASSWORD?)"

            exit(1)
    else:
        print "--Not logged in--"
    
    # This will fail because duckface is not a proper email, but you should get
    # past the authentication...
    try:
        try:
            print call(*args)
        except requests.exceptions.ConnectionError as e:
            print >> sys.stderr, "Could not connect with the given url '%s':" \
                    % config["api_url"]
            print >> sys.stderr, "\t" + str(e)

            exit(1)

    except RuntimeError as e:
        print str(e)
