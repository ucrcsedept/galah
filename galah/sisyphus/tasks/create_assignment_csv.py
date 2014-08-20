import shutil
import subprocess
import os
import datetime
import os.path
from bson import ObjectId

from galah.db.models import Submission, CSV, TestResult, User, Assignment

# Set up configuration and logging
from galah.base.config import load_config
config = load_config("sisyphus")

import logging
logger = logging.getLogger("galah.sisyphus.create_assignment_csv")

def _create_assignment_csv(csv_id, requester, assignment):
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
        assn = Assignment.objects.get(id = ObjectId(assignment))

        # Grab all student users for this class.
        users = list(
            User.objects(
                account_type = "student",
                classes = assn.for_class
            )
        )

        # Form the query
        query = {
            "assignment": ObjectId(assignment),
            "most_recent": True,
            "user__in": [i.id for i in users]
        }

        # Grab the most recent submissions from each user.
        submissions = list(Submission.objects(**query))

        # Create the actual csv file.
        csv_file = open(os.path.join(config["CSV_DIRECTORY"], str(csv_id)), "w")

        for i in submissions:
            score = "None"
            if i.test_results:
                test_result = TestResult.objects.get(id = i.test_results)
                score = str(test_result.score)

            print >> csv_file, "%s,%s,%s" % \
                (i.user, score, i.timestamp.strftime("%Y-%m-%d-%H-%M-%S"))

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
