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

import zmq

context = zmq.Context()

def send_task(heavylifter_host, task_name, *args, **kwargs):
    # We create a new socket and connect each time because sisyphus tasks
    # should not be sent very often, therefore it's not useful to hold an open
    # socket for large lengths of time without sending much of anything.
    socket = context.socket(zmq.REQ)
    socket.connect(heavylifter_host)

    try:
        socket.send_json({
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs
        })

        # Wait for a reply from the sisyphus.
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        if poller.poll(2 * 1000):
            reply = socket.recv_json()
        else:
            raise RuntimeError("sisyphus did not respond.")

        if not reply["success"]:
            raise RuntimeError(
                "sisyphus did not accept task.\n\t" + reply["error_string"]
            )
    finally:
        # Forcibly close the socket.
        socket.close(0)

#print send_task("ipc:///tmp/sisyphus.sock", "test_task", "hi")