# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

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
