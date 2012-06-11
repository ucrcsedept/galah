# Copyright 2012 John C. Sullivan, and Benjamin J. Kellogg
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

import universal, Queue, time, zmq, copy
from zmq.utils import jsonapi

def enqueue(zqueue, zitem, zpollTimeout = 5):
    """
    Puts an item into a queue. Blocks until ztimeout (indefinitely if None).
    Will raise Exiting exception if universal.exiting is True.
    
    """
    
    while not universal.exiting:
        try:
            zqueue.put(zitem, timeout = zpollTimeout)
            break
        except Queue.Full:
            pass
            
    if universal.exiting:
        raise universal.Exiting()

def dequeue(zqueue, zpollTimeout = 5):
    """
    Gets an item from a queue. Similar to enqueue.
    
    """
    
    while not universal.exiting:
        try:
            return zqueue.get(timeout = zpollTimeout)
        except Queue.Empty:
            pass

    raise universal.Exiting()
        
def recv_json(zsocket, ztimeout = None, zignoreExiting = False):
    """
    Recieves JSON from a socket. Assumes socket is set to timeout properly.
    Raises universal.Exiting if program is exiting, or zmq.ZMQError if
    timed out.
    """
    
    if ztimeout != None:
        startTime = time.clock()
    
    while (zignoreExiting or not universal.exiting) and \
          (ztimeout == None or startTime + ztimeout > time.clock()):
        try:
            print "luck"
            msg = zsocket.recv_multipart()
            print "duck"
            
            # Decode the json in the innermost frame
            msg[-1] = jsonapi.loads(msg[-1])
            
            # If only one frame was recieved simply return that frame
            if len(msg) == 1: msg = msg[0]
            
            return msg
        except zmq.ZMQError:
            print "chuck"
            pass
    
    if universal.exiting:
        raise universal.Exiting()
    else: # Must have timed out
        raise zmq.ZMQError()
    
def filterDictionary(zdict, zdesiredKeys):
    """
    Returns a copy of zdict with only the keys in zdesiredKeys.
    
    """
    
    # Create a copy of the dictionary
    zdictCopy = copy.deepcopy(zdict)
    
    for k in zdictCopy.keys():
        if k not in zdesiredKeys:
            del zdictCopy[k]
            
    return zdictCopy

def waitForQueue(zqueue, zpollTimeout = 5):
    """
    Blocks until a queue is not full or universal.exiting is True. Returns
    True if queue has available slot, raising universal.Exiting if program
    is exiting.
    
    """
    
    while not universal.exiting and zqueue.full():
        time.sleep(5)
    
    if universal.exiting:
        raise universal.Exiting()
    
    return True

def exit():
    universal.exiting = True
    
    raise universal.Exiting()
