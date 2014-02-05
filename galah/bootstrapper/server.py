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
from optparse import make_option, OptionParser

import logging
log = logging.getLogger("galah.bootstrapper.server")

# The interface and port to listen on
LISTEN_ON = ("", BOOTSTRAPPER_PORT)

def main(uds):
    if uds is not None:
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(uds)
    else:
        # If you're using TCP sockets for testing you might be tempted to use
        # the reuse addresses flag on the socket, I'd rather not deal with the
        # security problems there so just use UDS for testing.
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(LISTEN_ON)

    # The server will likely work just fine in blocking mode as well, but
    # we could get stuck in a deadlocked state if we're not careful. This is
    # due to the supposed fact that if select.select says that there's data
    # waiting to be read from a socket, that does not necessarily mean that you
    # won't block when you try.
    server_sock.setblocking(0)

    # Begin accepting new connections
    server_sock.listen(1)

    connections = []

    while True:
        # Block until one of the sockets we're looking at has data waiting to
        # be read or connections waiting to be accepted.
        socks, _w, _e = select.select([server_sock] + connections, [],
            [server_sock] + connections)
        log.debug("%r, %r", socks, _e)

        for sock in socks:
            try:
                if sock is server_sock:
                    # Accept any new connections
                    sock, address = server_sock.accept()
                    connections.append(Connection(sock))

                    log.info("New connection from %s", address)
                else:
                    for msg in sock.recv():
                        log.info("Received %s command with %d-byte payload",
                            msg.command, len(msg.payload))

                        response = handle_message(msg)
                        if response is not None:
                            log.info("Sending %s response with payload %r",
                                response.command, response.payload)
                            sock.send(response)
            except socket.error:
                log.warning("Exception raised on socket connected to %r",
                    sock.sock.getpeername(), exc_info = sys.exc_info())
                try:
                    sock.sock.shutdown(socket.SHUT_RDWR)
                    sock.sock.close()
                except:
                    pass
                connections.remove(sock)
            except Connection.Disconnected:
                log.info("%r disconnected", sock.sock.getpeername())
                connections.remove(sock)
            except Exception:
                log.error("Unknown exception raised while reading data from "
                    "%r", sock.sock.getpeername(), exc_info = sys.exc_info())
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

def setup_logging(log_dir):
    import codecs
    import tempfile
    import os
    import errno

    package_logger = logging.getLogger("galah.bootstrapper")

    # We'll let all log messages through to the handlers (though the handlers
    # can filter on another level if they'd like).
    package_logger.setLevel(logging.DEBUG)

    if log_dir == "-":
        # If we're not using a logfile, just log everythign to standard error
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(logging.Formatter(
            "[%(levelname)s;%(asctime)s]: %(message)s"
        ))
        package_logger.addHandler(stderr_handler)
    else:
        # If the directory we want to log to doesn't exist yet, create it
        try:
            os.makedirs(log_dir)
        except OSError as exception:
            # Ignore the "already exists" error but let through anything else
            if exception.errno != errno.EEXIST:
                raise

        # We'll let the tempfile module handle the heavy lifting of finding an
        # available filename.
        log_file = tempfile.NamedTemporaryFile(dir = log_dir,
            prefix = "bootstrapper.log-", delete = False)

        # We want to make sure the file is encoded using utf-8 so we wrap the
        # file object here to make the encoding transparent to the logging
        # library.
        log_file = codecs.EncodedFile(log_file, "utf_8")

        file_handler = logging.StreamHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "[%(levelname)s;%(asctime)s]: %(message)s"
        ))
        package_logger.addHandler(file_handler)

def parse_arguments(argv = sys.argv[1:]):
    option_list = [
        make_option(
            "--log-dir", action = "store", default = "/var/log/galah/",
            dest = "log_dir",
            help =
                "A directory that will hold the bootstrapper's log file. Can "
                "be - to log to standard error. Default %default."
        ),
        make_option(
            "--uds", action = "store", default = None,
            help =
                "If specified, the given unix domain socket will be created "
                "and listened on rather than binding to a port. Used during "
                "testing."
        )
    ]

    parser = OptionParser(option_list = option_list)

    options, args = parser.parse_args(argv)

    return (options, args)

if __name__ == "__main__":
    options, args = parse_arguments()

    setup_logging(options.log_dir)

    main(uds = options.uds)
