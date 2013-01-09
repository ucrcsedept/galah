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

import signal, sys, logging, threading, platform

# Will be set to True when the program is exiting.
exiting = False

# Thrown as an exception when a thread needs to exit
class Exiting:
    pass

# The Queue of containers that the producer will add to and the consumers will
# pull from.
containers = None

# The application-wide ZMQ context used to create sockets
context = None

# The command line options the user passes in
cmdOptions = None

# The system information sent to the Shepherd so it knows what kind of test
# requests we can safely process
environment = {
    "system": platform.system(),
    "release": platform.release(),
    "machine": platform.machine(),
    "tools": [
        {"name": "python", "version": platform.python_version()}
    ]
}

# Set it so that when we recieve a SIGINT we set exiting to True.
#def sigintHandler(a, b):
#    global exiting
#    exiting = True
#signal.signal(signal.SIGINT, sigintHandler)

# Create a decorator to allow thread's run functions to handle exiting
# exceptions.
_log = logging.getLogger("galah.sheep.universal")
def handleExiting(zfunc):
    def newFunc(*zargs, **zkwargs):
        try:
            zfunc(*zargs, **zkwargs)
        except Exiting:
            _log.info("%s's thread exited" % threading.currentThread().name)
    return newFunc
