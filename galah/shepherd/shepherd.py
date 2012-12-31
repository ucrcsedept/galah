# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
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

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("shepherd")

# Set up logging
import logging
logger = logging.getLogger("galah.shepherd")

# Connect to the mongo database
import mongoengine
mongoengine.connect(config["MONGODB"])

# The identities of all sheep waiting to be served a test request.
waiting_sheep = set()

# Create a queue that will keep track of waiting sheep and the waiting
# requests.
request_queue = []

# A class to store all of the known information about each sheep.
from collections import namedtuple
SheepInfo = namedtuple(
    "SheepInfo",
    [
        "environment",
        "last_bleet",
        "servicing_request",
        "began_servicing"
    ]
)

# A mapping from the sheeps' identities to their corresponding sheepinfo objects.
sheep_info = {}

import zmq
context = zmq.Context()

# Socket to communicate with sheep over
sheep = context.socket(zmq.ROUTER)
sheep.bind(config["SHEEP_SOCKET"])

# Socket to communicate with other components
public = context.socket(zmq.DEALER)
public.bind(config["PUBLIC_SOCKET"])

logger.info("Shepherd starting.")

SheepMessage = namedtuple("SheepMessage", ["type", "body"])

import json
def decode_sheep_message(message):
    # ValueError will be thrown if message is not a valid JSON object.
    message = json.loads(message)

    # Ensure the message has all the nessary components
    is_valid = (
        # Messages must be dictionaries/JSON objects.
        type(message) is dict and

        # Must have a type and a body.
        all(k in message for k in ("type", "body")) and

        # The type must be a string (may or may not be unicode)
        isinstance(message["type"], basestring) and

        # The message can either be a dictionary/JSON object, a string, or a
        # list/array (basically just can't be numeric)
        any(isinstance(type(message["body"]), t)
                for t in (dict, basestring, list))
    )

    if not is_valid:
        raise ValueError("Invalid sheep message.")

    return SheepMessage(message["type"], message["body"])

TestRequest = namedtuple(
    "TestRequest", 
    ["submission", "driver", "received_time"]
)

from galah.db.models import *
def decode_test_request(message):
    message = json.loads(message)

    is_valid = (
        type(message) is dict and
        "submission_id" in message and
        isinstance(message["submission_id"], basestring)
    )

    if not is_valid:
        raise ValueError("Invalid test request.")

    try:
        submission_id = ObjectId(message["submission_id"])
    except InvalidId:
        raise ValueError("Invalid submission id.")

    try:
        submission = Submission.objects.get(id = submission_id)
    except Submission.DoesNotExist:
        raise ValueError("Submission not found in database.")

    assignment = Assignment.objects.get(id = submission.assignment)

    return TestRequest(submission, assignment, datetime.datetime.today())

def main():
    while True:
        # Wait until either the public or sheep socket has messages waiting
        zmq.core.poll.select([public, sheep], [], [])

        # Will grab all of the outstanding messages from the outside and place them
        # in the request queue
        while public.getsockopt(zmq.EVENTS) & zmq.POLLIN != 0:
            request = outside.recv_multipart()
            logger.debug("Raw test request: %s", str(request_queue[-1]))

            try:
                request_queue.append(decode_test_request(request))
            except ValueError as e:
                logger.error("Could not decode test request: %s", str(e))
                logger.debug(
                    "Exception thrown while decoding...",
                    exc_info = sys.exc_info()
                )
                continue

            logger.info("Received test request.")

        # Will grab all of the outstanding messages from the sheep and process them
        while sheep.getsockopt(zmq.EVENTS) & zmq.POLLIN != 0:
            raw_message = sheep.recv_multipart()
            logger.debug("Raw sheep message: %s", str(raw_message))

            if len(raw_message) != 2:
                logger.error(
                    "Received incorrect number of frames (%d) from sheep.",
                    len(raw_message)
                )
                continue

            sheep_identity = raw_message[0]
            sheep_message = raw_message[1]
            
            try:
                sheep_message = decode_sheep_message(sheep_message)
            except ValueError as e:
                logger.error("Could not decode sheep's message: %s", str(e))
                logger.debug(
                    "Exception thrown while decoding...",
                    exc_info = sys.exc_info()
                )
                continue
            
            if sheep_message.type == "bleet":
                if sheep_identity not in sheep_info:
                    logger.info("Sheep bleeted before sending environment.")

                    # A signal should be sent to the sheep to tell it it needs to
                    # send environment information here.

                    continue

                waiting_sheep.add(sheep_identity)

                sheep_info[sheep_identity].last_bleet = datetime.datetime.today()

                logger.info("Sheep [%s] bleeted.", str(sheep_identity))
            elif sheep_message.type == "environment":
                if not isinstance(sheep_message.body, dict):
                    logger.error(
                        "Invalid environment (non-dict) received from sheep."
                    )
                    continue

                sheep_info[sheep_identity] = sheep_message.body
            elif sheep_message.type == "result":
                logger.info("Received test result from sheep.")
                logger.debug(
                    "Received test result from sheep: %s", str(sheep_message.body)
                )

        # Will return true if r is a subset of s.
        # > environments_match({"compiler": "g++"}, {"os": "unix", "compiler": "g++"})
        # True
        # > environments_match({"os": "unix", "compiler": "g++"}, {"compiler": "g++"})
        # False
        environments_match = lambda request, sheep: all(
            k in sheep.environment and sheep.environment[k] == v
                for k, v in request.environment.items()
        )

        # Attempt to match requests to waiting sheep. This loop executes in
        # O(n * m) time which should be acceptable for now but hopefully can be
        # improved on in the future.
        expired_requests = []
        for r_index in range(len(request_queue)):
            r = request_queue[r_index]

            # Check if any waiting sheep have the needed environment to handle
            # the request.
            for s in waiting_sheep:
                info = sheep_info[s]

                if environments_match(r.driver.environment, info.environment):
                    waiting_sheep.remove(s)

                    test_request = json.dumps(r)

                    sheep.send_multipart([sheep_identity, test_request])

                    sheep_info[sheep_identity].servicing_request = r
                    sheep_info[sheep_identity].began_servicing = \
                        datetime.datetime.today()

                    break
            else:
                if (datetime.datetime.today() - r.received_time >
                        config["REQUEST_QUEUE_TIMEOUT"]):
                    logger.warn("Request stayed in queue too long.")

                    expired_requests.append(r_index)

        # TODO: Need to add code to check if any sheep have been working on a
        # request for too long or they haven't bleeted in awhile. If they've
        # bleeted but they are still marked as having a request, this is
        # probably a sign that the shepherd messed up.

        # Remove all of the expired requests from the queue.
        request_queue = [
            i for j, i in enumerate(request_queue) if j not in expired_requests
        ]

main()