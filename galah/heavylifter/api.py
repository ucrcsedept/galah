import zmq

context = zmq.Context()

def send_task(heavylifter_host, task_name, *args, **kwargs):
    # We create a new socket and connect each time because heavylifter tasks
    # should not be sent very often, therefore it's not useful to hold an open
    # socket for large lengths of time without sending much of anything.
    socket = context.socket(zmq.REQ)
    socket.connect(heavylifter_host)

    socket.send_json({
        "task_name": task_name,
        "args": args,
        "kwargs": kwargs
    })

    # Wait for a reply from the heavylifter.
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(2 * 1000):
        reply = socket.recv_json()
    else:
        raise RuntimeError("heavylifter did not respond.")

    if not reply["success"]:
        raise RuntimeError(
            "heavylifter did not accept task.\n\t" + reply["error_string"]
        )

#print send_task("ipc:///tmp/heavylifter.sock", "test_task", "hi")