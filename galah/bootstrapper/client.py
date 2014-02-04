# This is necessary to allow relative imports from a script
if __name__ == "__main__" and __package__ is None:
    import galah.bootstrapper
    __package__ = "galah.bootstrapper"

import StringIO

from .protocol import *
import random

COMMANDS = set(["ping"])
"""The set of valid commands to send to the bootstrapper server."""

if __name__ == "__main__":
    import socket
    raw_sock = socket.create_connection(("localhost", 51749))
    sock = Connection(raw_sock, "localhost")

    sock.send(Message("ping", "good morning"))
    response = sock.recv()
    print response[0].payload, response[0].command



