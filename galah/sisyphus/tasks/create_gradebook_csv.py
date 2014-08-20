import shutil
import subprocess
import os
import datetime
import os.path
from bson import ObjectId

from galah.db.models import Assignment, Class, CSV, Submission, TestResult, User

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

# Set up configuration and logging
from galah.base.config import load_config
config = load_config("sisyphus")

import logging
logger = logging.getLogger("galah.sisyphus.create_gradebook_csv")

def _create_gradebook_csv(csv_id, requester, class_id, fill=0):
    csv_id = ObjectId(csv_id)

    csv_file = temp_directory = ""

    # Find any expired archives and remove them
    deleted_files = []
    for i in CSV.objects(expires__lt = datetime.datetime.today()):
        deleted_files.append(i.file_location)

        if i.file_location:
            try:
                os.remove(i.file_location)
            except OSError as e:
                logger.warning(
                    "Could not remove expired csv file at %s: %s.",
                    i.file_location, str(e)
                )

        i.delete()

    if deleted_files:
        logger.info("Deleted csv files %s.", str(deleted_files))

    # This is the CSV object that will be added to the database
    new_csv = CSV(
        id = csv_id,
        requester = requester
    )

    temp_directory = csv_file = None
    try:
        # Create the actual csv file.
        csv_file = open(os.path.join(config["CSV_DIRECTORY"], str(csv_id)), "w")

        the_class = Class.objects.get(id = ObjectId(class_id))

        # Grab all assignments in this class
        assns = list(
            Assignment.objects(for_class = the_class.id)
        )

        print >> csv_file, "%s,%s" % \
            ("Username", ",".join('"{0}"'.format(i.name) for i in assns))

        # Grab all student users for this class.
        users = list(
            User.objects(
                account_type = "student",
                classes = the_class.id
            )
        )

        assn_ids = [i.id for i in assns]
        for user in users:
            # Query for user's most recent submissions in the known assignments
            query = {
                "assignment__in": assn_ids,
                "most_recent": True,
                "user": user.id
            }

            submissions = list(Submission.objects(**query))

            # Initialize each assignment score to empty at first.
            assn_to_score = OrderedDict((i, str(fill)) for i in assn_ids)

            # Go through submissions, associating scores with assignment
            for sub in submissions:
                if sub.test_results:
                    test_result = TestResult.objects.get(id = sub.test_results)
                    if test_result.score is not None:
                        assn_to_score[sub.assignment] = str(test_result.score)

            # Write gradebook results to csv file.
            print >> csv_file, "%s,%s" % \
                (user.email, ",".join(assn_to_score.values()))

        csv_file.close()

        new_csv.file_location = os.path.join(config["CSV_DIRECTORY"], str(csv_id))

        new_csv.expires = \
            datetime.datetime.today() + config["TEACHER_CSV_LIFETIME"]

        new_csv.save(force_insert = True)
    except Exception as e:
        new_csv.file_location = None
        os.remove(os.path.join(config["CSV_DIRECTORY"], str(csv_id)))

        new_csv.error_string = str(e)
        new_csv.save(force_insert = True)

        raise
