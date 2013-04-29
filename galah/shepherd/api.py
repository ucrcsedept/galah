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

import zmq

context = zmq.Context()
context.linger = 2 * 1000

def send_test_request(shepherd_host, submission_id):
    # TODO: Make the socket thread-local.
    # Create a new socket to send a test request to shepherd.
    shepherd = context.socket(zmq.DEALER)

    shepherd.connect(shepherd_host)
    shepherd.send_json({
       "submission_id": str(submission_id)
    })

    shepherd.close()
