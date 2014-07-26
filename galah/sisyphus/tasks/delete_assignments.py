# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from galah.db.models import Assignment, Submission, Class, User
from bson import ObjectId
import os.path
import shutil
import errno

# Set up configuration and logging
from galah.base.config import load_config
config = load_config("sisyphus")

import logging
logger = logging.getLogger("galah.sisyphus.delete_assignments")

def _delete_assignments(ids, delete_class):
    if delete_class:
        delete_class = ObjectId(delete_class)

    # Convert all of the IDs we were given to ObjectIDs in one go
    ids = [ObjectId(i) for i in ids]

    logger.info("Deleting assignments %s.", str(ids))

    # Query the database for all the assignments we are supposed to delete
    assignments = list(Assignment.objects(id__in = ids))

    # Query the database for all the submissions we are supposed to delete, this
    # will potentially be an absolutely massive list, so we do not want to
    # place all the results into a list immediately like we did for the
    # assignments.
    submissions = Submission.objects(assignment__in = ids)

    # Delete assignments directory on the filesystem
    for i in assignments:
        try:
            shutil.rmtree(
                os.path.join(config["SUBMISSION_DIRECTORY"], str(i.id))
            )
        except OSError as e:
            # We don't want to explode if the directory has been deleted for us
            # but it is weird so log a warning.
            if e.errno == errno.ENOENT:
                logger.warning("Assignment directory missing for %s",
                    str(i.id))
            else:
                raise

    # Actually delete the submissions from the database
    Submission.objects(assignment__in = ids).delete()

    # Delete the assignments
    Assignment.objects(id__in = ids).delete()

    if delete_class:
        # Unenroll all students in the class
        User.objects(classes = delete_class).update(
            pull__classes = delete_class
        )

        # Delete the class
        Class.objects(id = delete_class).delete()
