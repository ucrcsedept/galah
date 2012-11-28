#!/usr/bin/env python

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
