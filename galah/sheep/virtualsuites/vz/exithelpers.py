# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

import datetime
from galah.sheep.virtualsuites.vz.vmpool import VMPool
import galah.sheep.utility.universal as universal

def enqueue(queue, item, poll_timeout = datetime.timedelta(seconds = 5)):
    while not universal.exiting:
        try:
            queue.put(item, timeout = poll_timeout)
            break
        except VMPool.Timeout:
            pass

    if universal.exiting:
        raise universal.Exiting()

def dequeue(queue, key, poll_timeout = datetime.timedelta(seconds = 5)):
    """
    Gets an item from a queue. Similar to enqueue.

    """

    while not universal.exiting:
        try:
            return queue.get(timeout = poll_timeout, key = key)
        except VMPool.Timeout:
            pass

    raise universal.Exiting()
