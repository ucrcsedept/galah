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

import logging
import galah.sheep.utility.universal as universal
import Queue
import utility
import pyvz
import time

@universal.handleExiting
def run():
    """
    Constantly creates new virtual machines.
    
    """
    
    log = logging.getLogger("galah.sheep.producer")
    
    log.info("Producer is starting")
    
    # Loop until the program is shutting down
    while not universal.exiting:
        log.info("Doing nothing.")

        time.sleep(10)