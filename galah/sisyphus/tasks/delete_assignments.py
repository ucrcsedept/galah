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
