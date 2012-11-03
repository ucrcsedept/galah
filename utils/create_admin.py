#!/usr/bin/env python

# First we need to get mongoengine connected to our mongo installation
import mongoengine
mongoengine.connect("galah")

# Grab whatever information we need from the user
import getpass
user_name = raw_input("What should the admin user name be (must be an email)? ")
password = getpass.getpass("What should this user's password be? ")

# Then we will access the create_user API command directly, and use the dummy
# user "admin_user" to fake a current user
from galah.api.commands import create_user, admin_user
create_user(admin_user, user_name, password, "admin")