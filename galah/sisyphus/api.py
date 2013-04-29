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

def send_task(sisyphus_host, task_name, *args, **kwargs):
    # We create a new socket and connect each time because sisyphus tasks
    # should not be sent very often, therefore it's not useful to hold an open
    # socket for large lengths of time without sending much of anything.
    socket = context.socket(zmq.REQ)
    socket.connect(sisyphus_host)

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
