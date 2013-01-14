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

import zmq
import galah.sheep.utility.universal as universal
import galah.sheep.utility.exithelpers as exithelpers
from galah.sheep.utility.suitehelpers import get_virtual_suite
from galah.base.flockmail import FlockMessage
import time
import threading
import logging
import random

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

class ShepherdLost(Exception):
    def __init__(self, current_request = None, result = None):
        self.current_request = current_request
        self.result = result

        Exception.__init__(self)

def bleet(socket, timeout, gap_time = 30 * 1000, fuzz_time = 2 * 1000):
    """
    Sends a bleet to the shepherd and responds to bloots. If any other type of
    message is received, it is returned as a tuple of address and the message
    itself. If nothing is received after the given timeout, a ShepherdLost
    exception is raised.

    gap_time is the amount of time between when a bloot is received before
    another bleet is sent, in milliseconds.

    fuzz_time is the number of milliseconds +/- gap_time that is an acceptable
    amount of time to wait.

    """

    logger = logging.getLogger("galah.sheep.%s" % threading.currentThread().name)

    while True:
        # Send a bleet
        socket.send_json(FlockMessage("bleet", "").to_dict())
        logger.debug("Sent bleet.")

        try:
            # Wait for a bloot
            message = exithelpers.recv_json(socket, timeout = timeout)
            message = FlockMessage.from_dict(message)
        except exithelpers.Timeout:
            raise ShepherdLost()

        if message.type == "bloot":
            logger.debug("Received bloot.")
            try:
                # Sleep for a certain amount of time unless another message
                # is received (probably a request) or until we're exiting.
                message = exithelpers.recv_json(
                    socket, 
                    timeout = gap_time +
                            random.randint(-fuzz_time, fuzz_time)
                )
                message = FlockMessage.from_dict(message)

                return message
            except exithelpers.Timeout:
                pass

            # Send another bleet
            continue
        else:
            return message

def send_result(socket, result, timeout):
    """
    Sends a test result to the shepherd and waits for confirmation.

    """

    logger = logging.getLogger("galah.sheep.%s" % threading.currentThread().name)

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    result_message = FlockMessage(
        type = "result",
        body = result
    )

    socket.send_json(result_message.to_dict())

    if poller.poll(timeout):
        message = exithelpers.recv_json(socket)
        message = FlockMessage.from_dict(message)

        if message.type == "bloot":
            if message.body != str(result["id"]):
                logger.error("Received bloot with incorrect ID.")
                raise ShepherdLost(result = result)
            else:
                return
        else:
            logger.error(
                "Received '%s' message with body '%s' from shepherd. Expected "
                "bloot.", str(message.type), str(message.body)
            )
            raise ShepherdLost(result = result)
    else:
        raise ShepherdLost(result = result)

@universal.handleExiting
def run():
    logger = logging.getLogger("galah.sheep.%s" % threading.currentThread().name)
    logger.info("Consumer starting.")

    # Initialize the correct consumer based on the selected virtual suite.
    virtual_suite = get_virtual_suite(config["VIRTUAL_SUITE"])
    consumer = virtual_suite.Consumer(logger)
    
    # Set up the socket to send/recieve messages to/from the shepherd
    shepherd = universal.context.socket(zmq.DEALER)
    shepherd.linger = 0
    shepherd.connect(config["shepherd/SHEEP_SOCKET"])
   
    # Loop until the program is shutting down
    while not universal.exiting:
        # Prepare a VM
        machine_id = consumer.prepare_machine()

        # Tell the shepherd we are ready for a test request
        logger.debug("Commencing bleets.")
        message = bleet(shepherd, 60 * 1000)
        logger.debug("Received message: %s", message)

        # If the shepherd asked for our environment information
        if message.type == "identify":
            logger.info("Received request to identify.")

            identification = FlockMessage(
                type = "environment",
                body = universal.environment
            )

            shepherd.send_json(identification.to_dict())
            continue

        if message.type != "request":
            logger.critical(
                "Unrecognized message type received. Version of sheep and "
                "shepherd are likely mismatched."
            )
            continue

        # Recieved test request from the shepherd
        logger.info("Test request received.")
        logger.debug("Test request: %s", str(message))

        result = consumer.run_test(machine_id, message.body)

        # Add in the submission id to the result that we send back
        result["id"] = str(message.body["submission"]["id"])

        send_result(shepherd, result, 30 * 1000)