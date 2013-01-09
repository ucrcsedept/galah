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

import shutil
import subprocess
import tempfile
import os
import datetime
from bson import ObjectId

from galah.db.models import Submission, Archive

# Set up configuration and logging
from galah.base.config import load_config
config = load_config("sisyphus")

import logging
logger = logging.getLogger("galah.sisyphus.tar_bulk_submissions")

def _tar_bulk_submissions(archive_id, requester, assignment, email = ""):
    archive_id = ObjectId(archive_id)

    archive_file = temp_directory = ""

    # Find any expired archives and remove them
    deleted_files = []
    for i in Archive.objects(expires__lt = datetime.datetime.today()):
        deleted_files.append(i.file_location)

        if i.file_location:
            try:
                os.remove(i.file_location)
            except OSError as e:
                logger.warning(
                    "Could not remove expired archive at %s: %s.",
                    i.file_location, str(e)
                )

        i.delete()

    if deleted_files:
        logger.info("Deleted archives %s.", str(deleted_files))

    # This is the archive object we will eventually add to the database
    new_archive = Archive(
        id = archive_id,
        requester = requester,
        archive_type = "assignment_package"
    )

    temp_directory = archive_file = None
    try:
        # Form the query
        query = {"assignment": ObjectId(assignment)}

        # Only mention email in the query if it's not None or the empty
        # string, otherwise mongo will look for submissions that list the
        # user as None or the empty string (which should be exactly none of
        # the submission in the system).
        if email:
            query["user"] = email

        # Grab all the submissions
        submissions = list(Submission.objects(**query))

        if not submissions:
            logger.info("No submissions found matching query.")
            return

        # Organize all the submissions by user name, as this will closely
        # match the structure of the archive we will build.
        submission_map = {}
        for i in submissions:
            if i.user in submission_map:
                submission_map[i.user].append(i)
            else:
                submission_map[i.user] = [i]

        # Create a temporary directory we will create our archive in.
        temp_directory = tempfile.mkdtemp()

        # Create our directory tree. Instead of making new folders for each
        # submission and copying the user's files over however, we will
        # create symlinks to save space and time.
        for user, user_submissions in submission_map.items():
            # Create a directory for the user
            os.makedirs(os.path.join(temp_directory, user))

            # Create symlinks for all his submissions. Each symlink is
            # named after the submission date.
            for i in user_submissions:
                time_stamp = i.timestamp.strftime("%Y-%m-%d-%H-%M-%S")
                symlink_path = \
                    os.path.join(temp_directory, user, time_stamp)

                # In the highly unlikely event that two of the same user's
                # submissions have the same exact time stamp, we'll need to
                # add a marker to the end of the timestamp.
                marker = 0
                while os.path.exists(symlink_path +
                        ("-%d" % marker if marker > 0 else "")):
                    marker += 1

                if marker > 0:
                    symlink_path += "-%d" % marker

                original_path = i.getFilePath()

                # Detect if the submission's files are still on the filesystem
                if os.path.isdir(original_path):
                    # Create a symlink pointing to the actual submission
                    # directory with the name we gnerated
                    os.symlink(original_path, symlink_path)
                else:
                    # Create an empty text file marking the fact that a
                    # submissions existed but is no longer available.
                    open(symlink_path, "w").close()

        # Create the actual archive file.
        # TODO: Create it in galah's /var/ directory
        file_descriptor, archive_file = tempfile.mkstemp(suffix = ".tar.gz")
        os.close(file_descriptor)

        # Run tar and do the actual archiving. Will block until it's finished.
        subprocess.check_call(
            [
                "tar", "--dereference", "--create", "--gzip", "--directory",
                temp_directory, "--file", archive_file
            ] + submission_map.keys()
        )

        new_archive.file_location = archive_file

        new_archive.expires = \
            datetime.datetime.today() + config["TEACHER_ARCHIVE_LIFETIME"]

        new_archive.save(force_insert = True)
    except Exception as e:
        # If we created a temporary archive file we need to delete it.
        new_archive.file_location = None
        if archive_file:
            os.remove(archive_file)

        new_archive.error_string = str(e)
        new_archive.save(force_insert = True)

        raise
    finally:
        if temp_directory:
            shutil.rmtree(temp_directory)