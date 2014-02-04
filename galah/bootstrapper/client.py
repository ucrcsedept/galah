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
    sock = socket.create_connection(("localhost", 51749))

    raw = serialize(Message("ping", "good morning"))
    sock.sendall(raw)
