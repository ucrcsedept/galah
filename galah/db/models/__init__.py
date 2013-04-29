# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

import mongoengine

# If were importing models from another component of galah the users shouldn't
# (and can't) be loaded.
try:
    import users
    from users import User

    import invitations
    from invitations import Invitation
except ImportError:
    pass

import classes
from classes import Class

import assignments
from assignments import Assignment, TestHarness

import submissions
from submissions import Submission, TestResult

import archives
from archives import Archive

import csv
from csv import CSV
