# This is necessary to allow relative imports from a script
if __name__ == "__main__" and __package__ is None:
    import galah.bootstrapper
    __package__ = "galah.bootstrapper"

# internal
from .protocol import *

# stdlib
import sys
import socket
import select

import logging
log = logging.getLogger("galah.bootstrapper.server")

# The interface and port to listen on
LISTEN_ON = ("", 51749)

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

    def read(self):
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

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This is useful during testing
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.setblocking(0)

    server_sock.bind(LISTEN_ON)
    server_sock.listen(2)

    connections = []

    while True:
        # Block until one of the sockets we're looking at has data waiting to
        # be read or connections waiting to be accepted.
        socks, _w, _e = select.select([server_sock] + connections, [], [server_sock] + connections)
        log.debug("%r, %r", socks, _e)

        for sock in socks:
            try:
                if sock is server_sock:
                    # Accept any new connections
                    sock, address = server_sock.accept()
                    connections.append(Connection(sock, address))

                    log.info("New connection from %s", address)
                else:
                    for msg in sock.read():
                        log.info("Received %s command with %d-byte payload",
                            msg.command, len(msg.payload))

                        response = handle_message(msg)
                        log.info("Sending %s response with payload %r",
                            response.command, response.payload)
                        sock.sock.sendall(serialize(response))
            except socket.error:
                log.warning("Exception raised on socket connected to %r",
                    sock.address, exc_info = sys.exc_info())
                try:
                    sock.sock.shutdown(socket.SHUT_RDWR)
                    sock.sock.close()
                except:
                    pass
                connections.remove(sock)
            except Connection.Disconnected:
                log.info("%r disconnected", sock.address)
                connections.remove(sock)
            except Exception:
                log.error("Unknown exception raised while reading data from "
                    "%r", sock.address, exc_info = sys.exc_info())
                try:
                    sock.sock.shutdown(socket.SHUT_RDWR)
                    sock.sock.close()
                except:
                    pass
                connections.remove(sock)

def handle_message(msg):
    if msg.command == u"ping":
        return Message("pong", msg.payload.decode("utf_8"))
    else:
        return Message("error", u"unknown command")

def setup_logging(use_logfile):
    import codecs
    import tempfile
    import os
    import errno

    package_logger = logging.getLogger("galah.bootstrapper")

    # We'll let all log messages through to the handlers (though the handlers
    # can filter on another level if they'd like).
    package_logger.setLevel(logging.DEBUG)

    if use_logfile:
        # Add log handler that spills logs into
        # /var/log/galah/bootstrapper.log-XXX
        LOG_DIR = "/var/log/galah/"
        try:
            os.makedirs(LOG_DIR)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # We'll let the tempfile module handle the heavy lifting of finding an
        # available filename.
        log_file = tempfile.NamedTemporaryFile(dir = LOG_DIR,
            prefix = "bootstrapper.log-", delete = False)
        log_file = codecs.EncodedFile(log_file, "utf_8")

        file_handler = logging.StreamHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "[%(levelname)s;%(asctime)s]: %(message)s"
        ))
        package_logger.addHandler(file_handler)
    else:
        # If we're not using a logfile, just log everythign to standard err
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(logging.Formatter(
            "[%(levelname)s;%(asctime)s]: %(message)s"
        ))
        package_logger.addHandler(stderr_handler)

if __name__ == "__main__":
    no_logfile = len(sys.argv) > 1 and sys.argv[1] == "--no-logfile"
    setup_logging(not no_logfile)

    main()
