# Copyright 2012 John Sullivan
# Copyright 2012 Other contributors as noted in the CONTRIBUTORS file
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

import logging
import galah.sheep.utility.universal as universal
from galah.sheep.utility.suitehelpers import get_virtual_suite
import Queue
import utility
import time

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

@universal.handleExiting
def run():
    """
    Constantly creates new virtual machines.
    
    """
    
    logger = logging.getLogger("galah.sheep.producer")
    
	# Initialize the correct producer based on the selected virtual suite.
    virtual_suite = get_virtual_suite(config["VIRTUAL_SUITE"])
    producer = virtual_suite.Producer(logger)

    logger.info("Producer is starting")
    
    # Loop until the program is shutting down
    while not universal.exiting:
        producer.produce_vm()