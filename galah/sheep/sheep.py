#!/usr/bin/env python



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

# Wait until we receive a SIGINT (a hook was added by universal.py that changes
# exiting to True when a SIGINT is received)
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
