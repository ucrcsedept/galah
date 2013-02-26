#!/usr/bin/env python

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

import threading

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

# Set up logging
import logging
logger = logging.getLogger("galah.sheep")

import zmq
import galah.sheep.utility.universal as universal
universal.context = zmq.Context()

import Queue
universal.orphaned_results = Queue.Queue()

# Initialize the correct consumer based on the selected virtual suite.
from galah.sheep.utility.suitehelpers import get_virtual_suite
virtual_suite = get_virtual_suite(config["VIRTUAL_SUITE"])
virtual_suite.setup(logger)

# Start the maintainer (who will start up the other threads)
import galah.sheep.components as components
maintainer = threading.Thread(target = components.maintainer.run,
                              args = (config["NCONSUMERS"], ),
                              name = "maintainer")
maintainer.start()

# Wait until we recieve a SIGINT (a hook was added by universal.py that changes
# exiting to True when a SIGINT is recieved)
from galah.sheep.utility.exithelpers import exitGracefully
import signal
signal.signal(signal.SIGINT, exitGracefully)
signal.signal(signal.SIGTERM, exitGracefully)

import time
try:
    while not universal.exiting:
        time.sleep(5)
except (SystemExit):
    universal.exiting = True

    print "Letting threads close... Don't spam Ctrl+C."

# Better idea. Set linger on each socket appropriately. Make sure all the
# threads shut down nicely here (but give an option to shut down immediately, a
# nice sleep that resumes when Ctrl+C is pressed should do nicely) within some
# configurable amount of time, and if they don't, set linger to zero and kill
# all the things.

logger.info("Sheep master ending...")
