#!/usr/bin/env python

# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
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

def main():
	# First we need to get mongoengine connected to our mongo installation
	import mongoengine
	mongoengine.connect("galah")

	# Grab whatever information we need from the user
	import getpass
	user_name = raw_input("What should the admin user name be (must be an email)? ")
	password = getpass.getpass("What should this user's password be? ")

	# Then we will access the create_user API command directly, and use the dummy
	# user "admin_user" to fake a current user
	from galah.web.api.commands import create_user, admin_user
	create_user(admin_user, user_name, password, "admin")

if __name__ == "__main__":
	main()
