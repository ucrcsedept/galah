import time
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

            time.sleep(30)
    except Exception as e:
        logger.error(str(e))

        raise
