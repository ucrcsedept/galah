import StringIO

import protocol
import random

COMMANDS = set(["ping"])
"""The set of valid commands to send to the bootstrapper server."""

if __name__ == "__main__":
    import socket
    sock = socket.create_connection(("localhost", 51749))

    while True:
        sock.sendall("".join(chr(random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])) for i in range(random.randint(0, 5000))))
