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
import time
import logging
import threading

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

@universal.handleExiting
def run():
    log = logging.getLogger("galah.sheep.%s" % threading.currentThread().name)

    log.info("Consumer starting.")
    
    # Set up the socket to recieve messages from the shepherd
    shepherd = universal.context.socket(zmq.DEALER)
    shepherd.linger = 0
    shepherd.connect(config["shepherd/SHEEP_SOCKET"])
                                      
    # First tell the Shepherd what kind of system this consumer is running on
    # and what kind of tests it supports.
    shepherd.send_json(universal.environment)
   
    # Loop until the program is shutting down
    while not universal.exiting:        
        # Tell the shepherd we are ready for a test request
        log.debug("Commencing bleet.")
        shepherd.send_json("bleet")
        log.debug("applesauce")
        # Recieve test request from the shepherd
        addresses = exithelpers.recv_json(shepherd)
        test_request = addresses.pop()
        log.info("Test request received.")
        log.debug("Test request: %s", str(test_request))

        log.debug("Pretending to do work.")
        time.sleep(10)

        shepherd.send_multipart(addresses + ["I am thy potatoe."])

        log.debug("Waiting for no reason...")
        time.sleep(20)