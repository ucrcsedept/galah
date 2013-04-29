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

import zmq, exiting, universal

def run(zsocket):
    while not exiting.exiting:
        # Wait for a message from the sheep
        address = zsocket.recv()
        zsocket.recv()
        body = zsocket.recv_json()

        if type(body) is str:
            # The sheep bleeted, add it to the queue
            universal.sheepQueue.append(address)
        else:
            # The sheep sent us environment information, note it
            universal.sheepEnvironments[address] = body

    raise exiting.Exiting()
