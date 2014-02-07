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

    def __repr__(self):
        formatted_payload = self.payload
        if len(formatted_payload) > 40:
            formatted_payload = repr(formatted_payload[:40]) + "..."
        else:
            formatted_payload = repr(formatted_payload)

        return "Message(command = %r, payload = %s)" % (self.command,
            formatted_payload)

def serialize(message):
    """
    Serializes a message into a ``str`` object suitable for sending over
    the wire. The encoded messages can be decoded by the decoder object at
    the other end.

    """

    buf = StringIO.StringIO()

    if not isinstance(message.payload, basestring):
        raise TypeError("payload must be str or unicode")

    # If the payload is a unicode string, we will encode it as UTF-8 (doing
    # this here is primarily for conveniece)
    if isinstance(message.payload, unicode):
        message.payload = message.payload.encode("utf_8")

    encoded_command = message.command.encode("ascii")
    if " " in encoded_command:
        raise ValueError("command cannot have spaces. Got %r" % (
            encoded_command))
    buf.write(encoded_command)
    buf.write(" ")

    num_bytes = len(message.payload)
    buf.write(str(num_bytes).encode("ascii"))
    buf.write(" ")

    buf.write(message.payload)

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

                # Make sure that we only switch into the payload state if we're
                # actually expecting a payload.
                if self._num_bytes != 0:
                    self.state = "PAYLOAD"
                    self._buffer_clear()
                else:
                    self.msg.payload = ""
                    full_command = self.msg
                    self.msg = Message()

                    self.state = "COMMAND"
                    self._buffer_clear()

                    return full_command
            else:
                self._buffer_write(character)
        elif self.state == "PAYLOAD":
            self._buffer_write(character)

            assert self.buffer_size <= self._num_bytes

            if self.buffer_size == self._num_bytes:
                self.msg.payload = self.buffer.getvalue()

                full_command = self.msg
                self.msg = Message()

                self.state = "COMMAND"
                self._buffer_clear()

                return full_command

        return None

class Connection(object):
    """
    :ivar sock: The ``socket`` instance returned by ``socket.accept()``.
    :ivar message_buffer: A ``list`` instance containing any messages received
        over the network but not yet returned by ``recv()``. Most recently
        recieved messages are at the front of the list, so
        ``message_buffer[-1]`` will be the next Message returned by ``recv()``.

    """

    class Disconnected(Exception):
        pass

    def __init__(self, sock):
        self.sock = sock

        self.message_buffer = []

        self._decoder = Decoder()

    # Necessary to support select.select()
    def fileno(self):
        return self.sock.fileno()

    def recv(self):
        """
        Reads a Message from the socket and returns it (or returns a Message
        that has already been received if any such Message is in the buffer).

        If the socket is in blocking mode, this function returns the oldest
        message in the message buffer if it is non-empty, otherwise it reads
        in data from the socket until a Message is decoded and then returns
        that Message.

        If the socket is in non-blocking mode this function will return the
        oldest message in the message buffer if such a message exists,
        otherwise it will read all of the data waiting in the socket and
        return the message it decodes, otherwise a socket.error or socket.
        timeout error will occur depending on how the socket is configured.

        """

        while not self.message_buffer:
            data = self.sock.recv(4096)
            if len(data) == 0:
                raise Connection.Disconnected()

            for i in data:
                msg = self._decoder.decode(i)
                if msg is not None:
                    log.debug("Received new %r message.", msg.command)
                    self.message_buffer.insert(0, msg)

        return self.message_buffer.pop()

    def send(self, message):
        """
        Sends the given Message across the connection.

        """

        self.sock.sendall(serialize(message))


    def shutdown(self):
        """
        Properly shuts down and closes the socket. Any errors are ignored.

        """

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
