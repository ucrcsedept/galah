import zmq
import galah.sheep.utility.universal as universal
import galah.sheep.utility.exithelpers as exithelpers
from galah.sheep.utility.suitehelpers import get_virtual_suite
from galah.base.flockmail import FlockMessage
import time
import threading
import logging
import random
import datetime

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

@universal.handleExiting
def run():
    try:
        _run()
    except universal.ShepherdLost as e:
        if e.result:
            universal.orphaned_results.put(e.result)

        raise

def _run():
    logger = logging.getLogger("galah.sheep.%s" % threading.currentThread().name)
    logger.info("Consumer starting.")

    # Initialize the correct consumer suite.
    virtual_suite = get_virtual_suite(config["VIRTUAL_SUITE"])
    consumer = virtual_suite.Consumer(logger)

    # Set up the socket to send/receive messages to/from the shepherd
    shepherd = universal.context.socket(zmq.DEALER)
    shepherd.linger = 0
    shepherd.connect(config["shepherd/SHEEP_SOCKET"])

    # Loop until the program is shutting down
    while not universal.exiting:
        # Prepare a VM and make sure we're completely prepared to handle a test
        # request before asking the shepherd for one.
        logger.info("Waiting for virtual machine to become available...")
        machine_id = consumer.prepare_machine()

        def bleet():
            shepherd.send_json(FlockMessage("bleet", "").to_dict())

            # Figure out when we should send the next bleet
            return (
                datetime.datetime.now() + config["shepherd/BLEET_TIMEOUT"] / 2
            )

        # Send the intitial bleet so that the shepherd knows we're available
        logger.info("Ready for test request. Sending initial bleet.")
        next_bleet_time = bleet()

        # Set to True whenever the shepherd bloots. Set to False everytime we
        # bleet. If this variable is still False by the time it's time to bleet
        # again we know we've lost the shepherd.
        shepherd_blooted = False

        # Process traffic from shepherd.
        while True:
            try:
                message = exithelpers.recv_json(
                    shepherd,
                    timeout = max(
                        1, # 1 millisecond (0 would imply infinite timeout)
                        (next_bleet_time - datetime.datetime.now()).seconds
                            * 1000
                    )
                )

                message = FlockMessage(message["type"], message["body"])
            except exithelpers.Timeout:
                if not shepherd_blooted:
                    raise universal.ShepherdLost()

                logger.debug("Sending bleet.")
                next_bleet_time = bleet()
                shepherd_blooted = False

                continue

            if message.type == "bloot":
                logger.debug("Got bloot.")
                shepherd_blooted = True

            elif message.type == "identify":
                logger.info(
                    "Received request to identify. Sending environment."
                )

                # identify is a valid response to a bleet.
                shepherd_blooted = True

                identification = FlockMessage(
                    type = "environment",
                    body = universal.environment
                )

                shepherd.send_json(identification.to_dict())

            elif message.type == "request":
                # Received test request from the shepherd
                logger.info("Test request received, running tests.")
                logger.debug("Test request: %s", str(message))
                result = consumer.run_test(machine_id, message.body)

                # Check to see if the test harness crashed/somehow testing was
                # unable to be done.
                if result is None:
                    result = {
                        "failed": True
                    }

                # Add in the submission id to the result that we send back
                result["id"] = str(message.body["submission"]["id"])

                logger.info("Testing completed, sending results to shepherd.")
                logger.debug("Raw test results: %s", str(result))
                shepherd.send_json(FlockMessage("result", result).to_dict())

                # Wait for the shepherd to acknowledge the result. Ignore any
                # messages that we get from the shepherd besides an acknowledge.
                deadline = \
                    datetime.datetime.now() + datetime.timedelta(seconds = 30)
                while True:
                    try:
                        confirmation = exithelpers.recv_json(
                            shepherd,
                            timeout = max(
                                1, # 1 millisecond (0 would imply infinite timeout)
                                (deadline - datetime.datetime.now()).seconds
                                    * 1000
                            )
                        )

                        confirmation = FlockMessage(
                            confirmation["type"], confirmation["body"]
                        )
                    except exithelpers.Timeout:
                        raise universal.ShepherdLost(result = result)

                    logger.debug("Received message: %s", str(confirmation))

                    if confirmation.type == "bloot" and \
                            confirmation.body == result["id"]:
                        shepherd_blooted = True
                        break

                break
