# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

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
