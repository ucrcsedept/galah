# stdlib
import StringIO

import logging
log = logging.getLogger("galah.bootstrapper.protocol")

BOOTSTRAPPER_PORT = 51749
"""The port the bootstrapper server will be listening on."""

class Message(object):
    """A message sent/to send over the Bootsrapper Protocol."""

    def __init__(self, command = None, payload = None):
        self.command = command
        self.payload = payload

def serialize(message):
    """
    Serializes a message into a ``str`` object suitable for sending over
    the wire. The encoded messages can be decoded by the decoder object at
    the other end.

    """

    buf = StringIO.StringIO()

    buf.write(message.command.encode("ascii"))
    buf.write(" ")

    num_bytes = len(message.payload)
    buf.write(str(num_bytes).encode("ascii"))
    buf.write(" ")

    payload = message.payload
    if isinstance(payload, unicode):
        payload = payload.encode("utf_8")
    buf.write(payload)

    return buf.getvalue()

class Decoder(object):
    """
    An object capable of decoding messages sent down the wire according to the
    Bootstrapper Protocol.

    """

    STATES = set(["COMMAND", "NUM_BYTES", "PAYLOAD"])

    def __init__(self):
        self.state = "COMMAND"
        self.msg = Message()
        self._num_bytes = 0
        self._buffer_clear()

    def _buffer_write(self, data):
        self.buffer.write(data)
        self.buffer_size += len(data)

    def _buffer_clear(self):
        self.buffer = StringIO.StringIO()
        self.buffer_size = 0

    def decode(self, character):
        """
        Attempts to decode the current message using the supplied character.

        :returns: None if the current message is not yet complete yet so
            cannot be fully decoded, or a Message object if the character was
            the final byte in the message.

        """

        assert self.state in self.STATES
        assert isinstance(character, str)
        assert len(character) == 1

        # We don't want to log the massive payloads
        if self.state != "PAYLOAD":
            log.debug("Decoding %r (state = %r, buffer = %r)", character,
                self.state, self.buffer.getvalue())

        if self.state == "COMMAND":
            if character == " ":
                self.msg.command = self.buffer.getvalue().decode("ascii")

                self.state = "NUM_BYTES"
                self._buffer_clear()
            else:
                self._buffer_write(character)
        elif self.state == "NUM_BYTES":
            if character == " ":
                decoded_data = self.buffer.getvalue().decode("ascii")
                self._num_bytes = int(decoded_data)

                self.state = "PAYLOAD"
                self._buffer_clear()
            else:
                self._buffer_write(character)
        elif self.state == "PAYLOAD":
            self._buffer_write(character)

            assert self.buffer_size <= self._num_bytes

            if self.buffer_size == self._num_bytes:
                self.msg.payload = self.buffer.getvalue()

                full_command = self.msg
                self.msg = Message()

                self._decoder_state = "COMMAND"
                self._buffer_clear()

                return full_command

        return None

class Connection(object):
    """
    :ivar sock: The ``socket`` instance returned by ``socket.accept()``.
    :ivar address: The address of the node at the other end of the connection.

    """

    class Disconnected(Exception):
        pass

    def __init__(self, sock, address):
        self.sock = sock
        self.address = address

        self._decoder = Decoder()

    # Necessary to support select.select()
    def fileno(self):
        return self.sock.fileno()

    def recv(self):
        """
        Reads in data waiting in the socket and returns a list of Message
        objects that were decoded.

        :returns: ``None``

        """

        data = self.sock.recv(4096)
        if len(data) == 0:
            raise Connection.Disconnected()

        messages = []
        for i in data:
            msg = self._decoder.decode(i)
            if msg is not None:
                messages.append(msg)
        return messages

    def send(self, message):
        """
        Sends the given Message across the connection.

        """

        self.sock.sendall(serialize(message))

