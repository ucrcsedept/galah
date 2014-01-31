import StringIO

BOOTSTRAPPER_PORT = 51749
"""
The port the bootstrapper will be listening on per the Boostrapper Protocol.

.. note::

    Do not change this value, it will not affect the port the bootstrapper is
    listening on. This value is only meant to be a reference.

"""

COMMANDS = set(["ping"])
"""The set of valid commands to send to the bootstrapper server."""

def serialize_message(command, payload):
    """
    Serializes a message according to the Bootstrapper Protocol.

    .. note::

        payload must be of type str and will not be translated in any way.

    """

    buf = StringIO.StringIO()

    buf.write(command.encode("ascii"))
    buf.write(" ")

    num_bytes = len(payload)
    buf.write(str(num_bytes).encode("ascii"))
    buf.write(" ")

    if not isinstance(payload, str):
        raise TypeError("payload must be a str object, got %s" % (
            type(payload).__name__))
    buf.write(payload)

    return buf.getvalue()

if __name__ == "__main__":
    import socket
    sock = socket.create_connection(("localhost", 51749))
    sock.sendall(serialize_message("hello", "bob"))
