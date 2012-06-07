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


import zmq, collections, zmq.utils

def routerRecv(zsocket, *zargs, **zkwargs):
    """
    Recieves a message that came in on a ROUTER socket.
    
    Returns a 3-tuple containing the address of the sender, any 'bulk' data
    (such as other address added onto the message by more routers along the
    way), and the actual body of the message, in that order.
    
    """
    
    message = zsocket.recv_multipart(*zargs, **zkwargs)
    
    # The last frame is the body and the first frame is the address of the
    # sender
    return (message[0], message[1:-1], message[-1])
    
def routerRecvJson(zsocket, *zargs, **zkwargs):
    address, bulk, body = routerRecv(zsocket, *zargs, **zkwargs)
    
    return (address, bulk, zmq.utils.jsonapi.loads(body))
    
def routerSend(zsocket, zaddress, zbulk, zbody, *zargs, **zkwargs):
    if zbulk == None: zbulk = ()
    
    zsocket.send_multipart((zaddress,) + tuple(zbulk) + (zbody,), *zargs,
                           **zkwargs)

def routerSendJson(zsocket, zaddress, zbulk, zbody, *zargs, **zkwargs):
    routerSend(zsocket, zaddress, zbulk, zmq.utils.jsonapi.dumps(zbody), 
               *zargs, **zkwargs)

# Create a queue that will keep track of waiting sheep
sheepQueue = collections.deque()

# A map from sheep to their environment information
sheepEnvironments = {}

context = zmq.Context()

# Socket to send Test Requests to galah-test
sheep = context.socket(zmq.ROUTER)
sheep.bind("tcp://*:6667")

# Socket to recieve Test Requests from the other components
outside = context.socket(zmq.ROUTER)
outside.bind("tcp://*:6668")

while True:
    # For now, take in tasks from stdin
    address, bulk, test_request = routerRecv(outside)
    
    print "Recieved test request:", test_request
    
    # Will continue looping until the queue has something in it and there are
    # no more outstanding messages
    while not (sheepQueue and sheep.poll(1) == 0):
        address, bulk, body = routerRecvJson(sheep)
        
        # TODO: The bulk is discarded, and this isn't bad as handling it would
        #       be difficult, but if I want to support crazier routing schemes
        #       I'll need to fix this.
        
        if type(body) is unicode:
            # The sheep bleeted (signalying it wants more work) so add it to
            # the queue
            sheepQueue.append(address)
            print "Sheep bleeted ", body
        else:
            # The sheep sent us environmental information, note it
            sheepEnvironments[address] = body
            print "Sheep connected ", body
    
    # Note here I have not validated the test_request. This is by design, the
    # shepherd should not concern itself with such things
    routerSend(sheep, sheepQueue.popleft(), (), test_request)
