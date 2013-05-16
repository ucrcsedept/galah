# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributors as noted in the CONTRIBUTORS file
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

import galah.sheep.utility.universal as universal
import galah.sheep.utility.exithelpers as exithelpers
from galah.base.flockmail import FlockMessage
import threading
import logging
import consumer
import producer
import time
import zmq

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

# Set up logging
import logging
logger = logging.getLogger("galah.sheep.maintainer")

poll_timeout = 10

# A counter used to generate names for consumer threads, not guarenteed to be
# the number of consumers currently extant.
_consumer_counter = 0
def start_consumer():
    global _consumer_counter

    consumerThread = threading.Thread(target = consumer.run,
                                      name = "consumer-%d" % _consumer_counter)
    consumerThread.start()

    _consumer_counter += 1

    return consumerThread

def start_producer():
    producer_thread = threading.Thread(target = producer.run, name = "producer")
    producer_thread.start()

    return producer_thread

@universal.handleExiting
def run(znconsumers):
    log = logging.getLogger("galah.sheep.maintainer")

    log.info("Maintainer starting")

    producer = start_producer()
    consumers = []

    # Continually make sure that all of the threads are up until it's time to
    # exit
    while not universal.exiting:
        if not universal.orphaned_results.empty():
            logger.warning(
                "Orphaned results detected, going into distress mode."
            )

        while not universal.orphaned_results.empty():
            try:
                # We want to create a whole new socket everytime so we don't
                # stack messages up in the queue. We also don't want to just
                # send it once and let ZMQ take care of it because it might
                # be eaten by a defunct shepherd and then we'd be stuck forever.
                shepherd = universal.context.socket(zmq.DEALER)
                shepherd.linger = 0
                shepherd.connect(config["shepherd/SHEEP_SOCKET"])

                shepherd.send_json(FlockMessage("distress", "").to_dict())

                logger.info(
                    "Sent distress message to shepherd, waiting for response."
                )

                message = exithelpers.recv_json(shepherd, timeout = 1000 * 60)
                message = FlockMessage.from_dict(message)

                if message.type == "bloot" and message.body == "":
                    while not universal.orphaned_results.empty():
                        result = universal.orphaned_results.get()

                        try:
                            shepherd.send_json(
                                FlockMessage("result", result).to_dict()
                            )

                            confirmation = exithelpers.recv_json(
                                shepherd, timeout = 1000 * 5
                            )
                            confirmation = FlockMessage.from_dict(confirmation)

                            if confirmation.type == "bloot" and \
                                    confirmation.body == "":
                                continue
                        except:
                            universal.orphaned_results.put(result)
                            raise
            except universal.Exiting:
                logger.warning(
                    "Orphaned results have not been sent back to the "
                    "shepherd. I WILL NOT ABANDON THEM, YOU WILL HAVE TO "
                    "KILL ME WITH FIRE! (SIGKILL is fire in this analogy)."
                )

                # Nah man.
                universal.exiting = False

                continue
            except exithelpers.Timeout:
                continue

        # Remove any dead consumers from the list
        dead_consumers = 0
        for c in consumers[:]:
            if not c.isAlive():
                dead_consumers += 1
                consumers.remove(c)

        if dead_consumers > 0:
            logger.warning(
                "Found %d dead consumers, restarting them.", dead_consumers
            )

        # Start up consumers until we have the desired amount
        while len(consumers) < znconsumers:
            consumers.append(start_consumer())

        # If the producer died, start it again
        if not producer.isAlive():
            log.warning("Found dead producer, restarting it.")

            producer = start_producer()

        # Sleep for awhile
        time.sleep(poll_timeout)

    raise universal.Exiting()
