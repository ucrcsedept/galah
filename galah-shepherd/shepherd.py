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

import zmq, collections, zmq.utils, logging, json, datetime
from app.models import *
from bson.objectid import ObjectId
from mongoengine import *

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
class SheepInfo:
    def __init__(self, zenvironment):
        self.environment = zenvironment
        
        self.servicingRequest = None
        self.beganServicing = None
sheepInfo = {}

# A map from sheep to the submission they're servicing
sheepAssignments = {}

context = zmq.Context()

# Socket to send Test Requests to galah-test
sheep = context.socket(zmq.ROUTER)
sheep.setsockopt(ZMQ_RCVTIMEO, 1 * 1000)
sheep.bind("tcp://*:%d" % cmdOptions.sheepPort)

# Socket to recieve Test Requests from the other components
outside = context.socket(zmq.ROUTER)
outside.setsockopt(ZMQ_RCVTIMEO, 1 * 1000)
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
            rawMessage = sheep.recv_multipart()
            sheepAddress, sheepEnvelope, sheepMessage = \
                (rawMessage[0], rawMessage[1:-1], rawMessage[-1])
                
            sheepMessage = json.loads(sheepMessage)
        except zmq.ZMQError:
            # Timed out
            break
        
        if isinstance(sheepMessage, basestring):
            # The sheep bleeted (signalying it wants more work) so add it to
            # the queue
            sheepQueue.append(sheepAddress)
            
            log.debug("Sheep bleeted")
        elif isinstance(sheepMessage, dict) and "system" in sheepMessage:
            # The sheep sent us environmental information, note it
            sheepInfo[sheepAddress] = SheepInfo(sheepMessage)
            
            log.info("Sheep connected with environment information " + str(sheepMessage))
        else:
            # The sheep sent us a test result
            log.debug("Sheep sent test result " + str(sheepMessage))
            
            testResult = submissions.TestResult(**sheepMessage)
            
            # Pull down the submission the TestResult was for
            submission = Submission.objects.get(
                id = ObjectId(sheepInfo[sheepAddress].servicingRequest["_id"]["value"])
            )
            
            # Add the test result to it
            submission.testResult = testResult
            
            try:
                # Save the submission to the database
                submission.save()
                
                log.debug("Test result is valid.")
            except ValidationError, e:
                log.warn("Test result is invalid.", exc_info = True)
                log.debug(str(e.errors))

    # Will match as many requests to sheep as possible
    while requestQueue and sheepQueue:
        sheepAddress = sheepQueue.popleft()
        request = requestQueue.popleft()
        
        # Convert the submission into a proper test request that the sheep knows
        # how to read
        submission = json.loads(request.pop())
        assignment = Assignment.objects.get(id = ObjectId(submission["assignment"]["value"]))
        
        test_request = {
            "testables": submission["testables"],
            "testDriver": assignment.testSpecification.testDriver,
            "timeout": assignment.testSpecification.timeout,
            "actions": assignment.testSpecification.actions,
            "config": assignment.testSpecification.config
        }
        
        request.append(json.dumps(test_request))
        
        # Send the test request to the sheep
        message = [sheepAddress] + request
        sheep.send_multipart(message)
        
        # Note that the sheep is doing work
        sheepInfo[sheepAddress].servicingRequest = submission
        sheepInfo[sheepAddress].beganServicing = datetime.datetime.now()
        
        log.debug("Sent request to sheep: " + str(message))
