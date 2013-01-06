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

import galah.sheep.utility.universal as universal
import threading
import logging
import consumer
import producer
import time

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
