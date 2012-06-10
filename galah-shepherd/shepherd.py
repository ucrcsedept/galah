# Copyright 2012 John C. Sullivan
# 
# This file is part of Galah.
# 
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Galah. If not, see <http://www.gnu.org/licenses/>.

import zmq, collections, zmq.utils, logging

# ZMQ constants for timeouts which are inexplicably missing from pyzmq
ZMQ_RCVTIMEO = 27
ZMQ_SNDTIMEO = 28

## Parse Command Line Arguments ##
from optparse import OptionParser, make_option

optionList = [
    make_option("--sheep-port", dest = "sheepPort", default = 6667,
                metavar = "PORT", type = "int",
                help = "Listen for sheep on port PORT (default: %default)"),
                
    make_option("--public-port", dest = "publicPort", default = 6668,
                metavar = "PORT", type = "int", 
                help = "Listen for requests on port PORT (default: %default)"),

    make_option("-l", "--log-level", dest = "logLevel", type = "int",
                default = logging.DEBUG, metavar = "LEVEL",
                help = "Only output log entries above LEVEL (default: "
                       "%default)"),

    make_option("-q", "--quiet", dest = "verbose", action = "store_false",
                default = True,
                help = "Don't output logging messages to stdout")
]
                  
parser = OptionParser(
    description = "Acts as a router that delgates test requests from Galah's "
                  "other components to galah-test servers.",
    version = "alpha-1",
    option_list = optionList
)

cmdOptions = parser.parse_args()[0]

## Main ##

# Set up logging
if cmdOptions.verbose:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s.%(levelname)s: %(message)s"))
    topLog = logging.getLogger("galah")
    topLog.setLevel(cmdOptions.logLevel)
    topLog.addHandler(sh)

log = logging.getLogger("galah.shepherd")

# Create a queue that will keep track of waiting sheep
sheepQueue = collections.deque()

# Create a queue that will keep track of the waiting requests
requestQueue = collections.deque()

# A map from sheep to their environment information
sheepEnvironments = {}

context = zmq.Context()

# Socket to send Test Requests to galah-test
sheep = context.socket(zmq.ROUTER)
sheep.setsockopt(ZMQ_RCVTIMEO, 5 * 1000)
sheep.bind("tcp://*:%d" % cmdOptions.sheepPort)

# Socket to recieve Test Requests from the other components
outside = context.socket(zmq.ROUTER)
outside.setsockopt(ZMQ_RCVTIMEO, 5 * 1000)
outside.bind("tcp://*:%d" % cmdOptions.publicPort)

log.info("Shepherd starting")

while True:
    # Will grab all of the outstanding messages from the outside and place them
    # in the request queue
    while True:
        try:
            request = outside.recv_multipart()
            requestQueue.append(request)
            
            log.debug("Recieved test request: " + request[-1])
        except zmq.ZMQError:
            # Timed out
            break
    
    # Will grab all of the outstanding messages from the sheep and process them
    while True:
        # Recieve a message from the sheep. Note this will fail if the sheep's
        # message picked up any other addresses (from other routers for
        # example).
        try:
            sheepAddresses, sheepMessage = sheep.recv_multipart()
        except zmq.ZMQError:
            # Timed out
            break
        
        if type(sheepMessage) is unicode:
            # The sheep bleeted (signalying it wants more work) so add it to
            # the queue
            sheepQueue.append(sheepAddresses)
            
            log.debug("Sheep bleeted " + sheepMessage)
        else:
            # The sheep sent us environmental information, note it
            sheepEnvironments[sheepAddress] = sheepMessage
            
            log.info("Sheep connected " + sheepMessage)

    # Will match as many requests to sheep as possible
    while requestQueue and sheepQueue:
        message = [sheepQueue.popleft()] + [requestQueue.popleft()]
        sheep.send_multipart(message)
        
        log.debug("Sent to sheep: " + message)
