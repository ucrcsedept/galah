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

import datetime
from bson import ObjectId

from galah.db.models import Submission, Assignment

# Set up configuration and logging
from galah.base.config import load_config
from galah.shepherd.api import send_test_request
config = load_config("sisyphus")
shepherd_config = load_config("shepherd")

import logging
logger = logging.getLogger("galah.sisyphus.rerun_test_harness")

def _rerun_test_harness(assignment):
    try:
        # Get assignment
        assn = Assignment.objects.get(id = ObjectId(assignment))

        if not assn.test_harness:
            logger.info("Attempting to rerun test harnesses on assignment "
                        "with no test harnesses")
            return

        # Form the submissions query
        query = {
            "assignment": ObjectId(assignment),
            "most_recent": True
        }

        # Grab the most recent submissions from each user.
        submissions = list(Submission.objects(**query))

        if not submissions:
            logger.info("No submissions found for this assignment.")
            return

        # Send a bunch of test requests to shepherd to be rerun.
        for i in submissions:
            i.test_request_timestamp = datetime.datetime.now()
            i.save()
            logger.info("Sent test request to shepherd for %s" % str(i.id))
            send_test_request(shepherd_config["PUBLIC_SOCKET"], i.id)
    except Exception as e:
        logger.error(str(e))

        raise
