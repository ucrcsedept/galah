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

def main():
    # FIgure out what to delete.
    delete_submissions = raw_input(
        "Are you sure you want to delete all submissions? ") == "yes"
    delete_assignments = delete_submissions and raw_input(
        "Are you sure you want to delete all assignments? ") == "yes"
    delete_users = delete_assignments and raw_input(
        "Are you sure you want to delete all non-admin users? ") == "yes"
    delete_classes = delete_users and raw_input(
        "Are you sure you want to delete all classes? ") == "yes"

    # First we need to get mongoengine connected to our mongo installation
    import mongoengine
    mongoengine.connect("galah")

    from galah.base.config import load_config
    config = load_config("global")

    if delete_submissions:
        # Delete all of the submissions from the filesystem
        import subprocess
        print "Deleting all submissions from the filesystem..."
        subprocess.check_call(["rm", "-r", config["SUBMISSION_DIRECTORY"]])
    
        import galah.db.models as models

        # Delete all of the submissions from the database. Submissions point to
        # both users and assignments, so they must be deleted before both.
        print "Deleting all submissions from the database..."
        models.Submission.objects().delete()

    if delete_users:
        # Delete all of the non-admin users from the database. Users point to
        # classes.
        print "Deleting all non-admin users from the database..."
        models.User.objects(account_type__ne = "admin").delete()

    if delete_assignments:
        # Delete all of the assignments from the database. Assignments point to
        # classes.
        print "Deleting all assignments from the database..."
        models.Assignment.objects().delete()

    if delete_classes:
        # Delete all of the classes from the database.
        print "Deleting all classes from the database..."
        models.Class.objects().delete()

if __name__ == "__main__":
    main()
