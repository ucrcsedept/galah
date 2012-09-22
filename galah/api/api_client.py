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

    return parser.parse_args(args)

import os
if __name__ == "__main__":
    options, args = parse_arguments()

    if options.user:
        try:
            print login(options.user, os.environ.get("GALAH_PASSWORD"))
        except RuntimeError:
            print "Could not log in with provided user name and password. "\
                  "(Did you remember to set GALAH_PASSWORD?)"

            exit(1)
    
    # This will fail because duckface is not a proper email, but you should get
    # past the authentication...
    try:
        print call(*args)
    except RuntimeError as e:
        print str(e)
