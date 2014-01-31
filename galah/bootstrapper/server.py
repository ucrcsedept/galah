# stdlib
import socket
import select
import StringIO

# The interface and port to listen on
LISTEN_ON = ("", 51749)

class Message(object):
    def __init__(self, command = None, num_bytes = None, payload = None):
        self.command = command
        self.num_bytes = num_bytes
        self.payload = payload

class Decoder(object):
    """
    An object capable of decoding messages sent down the wire according to the
    Bootstrapper Protocol.

    """

    STATES = set(["COMMAND", "NUM_BYTES", "PAYLOAD"])

    def __init__(self):
        self.state = "COMMAND"
        self.msg = Message()
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

        print repr(character), repr(self.state), repr(self.buffer.getvalue())

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
                self.msg.num_bytes = int(decoded_data)

                self.state = "PAYLOAD"
                self._buffer_clear()
            else:
                self._buffer_write(character)
        elif self.state == "PAYLOAD":
            self._buffer_write(character)

            assert self.buffer_size <= self.msg.num_bytes

            if self.buffer_size == self.msg.num_bytes:
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

    def __init__(self, sock, address):
        self.sock = sock
        self.address = address

        self._decoder = Decoder()

    # Necessary to support select.select()
    def fileno(self):
        return self.sock.fileno()

    def read(self):
        """
        Reads in data waiting in the socket and returns a list of Message
        objects that were decoded.

        :returns: ``None``

        """

        messages = []
        data = self.sock.recv(4096)
        for i in data:
            msg = self._decoder.decode(i)
            if msg is not None:
                messages.append(msg)
        return messages

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This is useful during testing
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind(LISTEN_ON)
    server_sock.listen(2)

    connections = []

    while True:
        # Block until one of the sockets we're looking at has data waiting to
        # be read or connections waiting to be accepted.
        socks, _w, _e = select.select([server_sock] + connections, [], [])

        for sock in socks:
            if sock is server_sock:
                # Accept any new connections
                sock, address = server_sock.accept()
                connections.append(Connection(sock, address))

                print "New connection from", address
            else:
                for msg in sock.read():
                    print "Got message:", msg

if __name__ == "__main__":
    main()
