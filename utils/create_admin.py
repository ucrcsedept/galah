#!/usr/bin/env python

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

def create_admin(email, password, galah_server = "galah"):
    # First we need to get mongoengine connected to our mongo installation
    import mongoengine
    mongoengine.connect(galah_server)

    # Then we will access the create_user API command directly, and use the
    # dummy user "admin_user" to fake a current user
    from galah.web.api.commands import create_user, admin_user
    create_user(admin_user, email, password, "admin")

import sys
def parse_arguments(args = sys.argv[1:]):
    from optparse import OptionParser, make_option

    option_list = [
        make_option(
            "--password-env", "-e", metavar = "VARIABLE_NAME",
            dest = "password_env",
            help = "The name of an environmental variable to pull the password "
                   "for the new admin user from."
        )
    ]

    parser = OptionParser(
        usage = "Usage: %prog [OPTIONS] EMAIL [PASSWORD]",
        description = "Command line interface to Galah for use by instructors "
                      "and administrators. If PASSWORD is not specified and "
                      "-p is not specified, user will be prompted for the "
                      "password.",
        option_list = option_list
    )

    options, pos_args = parser.parse_args(args)

    if len(pos_args) != 1 and len(pos_args) != 2:
        parser.error(
            "Exactly 1 or 2 positional arguments may be supplied, %d given." %
                len(pos_args)
        )

    return (options, pos_args)

def main():
    options, args = parse_arguments()

    if len(args) == 2:
        password = args[1]
    elif options.password_env:
        import os
        password = os.environ.get(options.password_env)

        if not password:
            print >> sys.stderr, (
                "Could not get password from environmental variable %s." %
                    options.password_env
            )

            return 1
    else:
        # Grab the password from the user.
        import getpass
        password = getpass.getpass("What should this user's password be? ")

        if not password:
            print >> sys.stderr, "No password given. Aborting."

            return 1

    print "Creating admin user", args[0]
    try:
        create_admin(args[0], password)
    except Exception as e:
        print >> sys.stderr, "Could not create admin user.", str(e)

        return 1

    return 0

if __name__ == "__main__":
    exit(main())
