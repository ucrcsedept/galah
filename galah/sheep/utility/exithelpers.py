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

import universal, Queue, time, zmq, copy, time
from zmq.utils import jsonapi

class Timeout(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


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
        
def recv_json(socket, timeout = None, ignore_exiting = False):
    """
    Recieves JSON from a socket. Assumes socket is set to timeout properly.
    Raises universal.Exiting if program is exiting, or zmq.ZMQError if
    timed out.
    """

    # Wait for a reply from the sisyphus.
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    
    if timeout is not None:
        start_time = time.time()

    poll_wait_time = 1000 if timeout is None else min(timeout, 1000)
    while ignore_exiting or not universal.exiting:
        if poller.poll(poll_wait_time):
            msg = socket.recv_multipart()
            
            # Decode the json in the innermost frame
            msg[-1] = jsonapi.loads(msg[-1])
            
            # If only one frame was recieved simply return that frame
            if len(msg) == 1: msg = msg[0]
            
            return msg
        elif timeout is not None and start_time + timeout <= time.time():
            raise Timeout()
    
    raise universal.Exiting()

def waitForQueue(zqueue, zpollTimeout = 5):
    """
    Blocks until a queue is not full or universal.exiting is True. Returns
    True if queue has available slot, raising universal.Exiting if program
    is exiting.
    
    """
    
    while not universal.exiting and zqueue.full():
        time.sleep(zpollTimeout)
    
    if universal.exiting:
        raise universal.Exiting()
    
    return True

def exit():
    universal.exiting = True
    
    raise universal.Exiting()
