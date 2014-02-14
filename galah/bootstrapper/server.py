# This is necessary to allow relative imports from a script
if __name__ == "__main__" and __package__ is None:
    import galah.bootstrapper
    __package__ = "galah.bootstrapper"

# internal
from .protocol import *

# stdlib
from optparse import make_option, OptionParser
import sys
import socket
import select
import errno
import json
import tempfile
import subprocess
import os
import zipfile
import pwd
import grp
import fcntl
import datetime

import logging
log = logging.getLogger("galah.bootstrapper.server")

# The interface and port to listen on
LISTEN_ON = ("", BOOTSTRAPPER_PORT)

config = None
"""The global configuration dictionary. Set by the ``init`` command."""

class UntrustedConnection(Connection):
    """
    A normal protocol.Connection object for all purposes except that it also
    has the boolean instance variable ``authenticated`` that stores whether the
    peer has sent an appropriate ``auth`` command.

    """

    def __init__(self, *args, **kwargs):
        self.authenticated = False

        super(UntrustedConnection, self).__init__(*args, **kwargs)

def process_socket(sock, server_sock, connections):
    """
    A helper function used by ``main()`` to correctly read from its sockets.

    The arguments are meant to match the variables in the main function.

    """

    if sock is server_sock:
        # Accept any new connections
        sock, address = server_sock.accept()
        sock.setblocking(0)
        connections.append(UntrustedConnection(sock))

        log.info("New connection from %s", address)
    else:
        while True:
            try:
                msg = sock.recv()
            except socket.error as e:
                if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                    # There is no more data in the socket
                    break
                else:
                    # Something else happened so let it bubble up
                    raise

            log.info("Received %s command from %s with %d-byte payload",
                msg.command, sock.sock.getpeername(), len(msg.payload))

            response = handle_message(msg, sock)
            if response is not None:
                log.info("Sending %s response with payload %r",
                    response.command, response.payload)
                sock.send(response)

                if response.command == "error":
                    log.info("Disconnecting from %s", sock.sock.getpeername())
                    sock.shutdown()
                    connections.remove(sock)
                    return

def main(uds = None):
    """
    Executes the main logic of the server.

    :param uds: If ``None``, the server will listen on the TCP address-port
        pair specified by ``LISTEN_ON``, otherwise this argument will be
        treated as a path to a unix domain socket which will be created and
        listened on.

    """

    if uds is not None:
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(uds)
    else:
        # If you're using TCP sockets for testing you might be tempted to use
        # the reuse addresses flag on the socket, I'd rather not deal with the
        # security problems there so just use UDS for testing.
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(LISTEN_ON)

    server_sock.setblocking(0)

    # Begin accepting new connections
    server_sock.listen(1)

    connections = []

    while True:
        # Block until one of the sockets we're looking at has data waiting to
        # be read or connections waiting to be accepted.
        socks, _w, _e = select.select([server_sock] + connections, [], [])
        log.debug("%d sockets out of %d with data waiting.", len(socks), len(connections))

        for sock in socks:
            try:
                # There's quite a bit of stuff we have to do here and the
                # nesting becomes a problem so I moved the code to a helper
                # function.
                process_socket(sock, server_sock, connections)
            except socket.error:
                log.warning("Exception raised on socket connected to %r",
                    sock.sock.getpeername(), exc_info = sys.exc_info())
                sock.shutdown()
                connections.remove(sock)
            except UntrustedConnection.Disconnected:
                log.info("%r disconnected", sock.sock.getpeername())
                sock.shutdown() # Just in case
                connections.remove(sock)
            except Exception:
                log.error("Unknown exception raised while reading data from "
                    "%r", sock.sock.getpeername(), exc_info = sys.exc_info())
                sock.shutdown()
                connections.remove(sock)

def safe_extraction(zipfile, dir_path):
    """
    Extracts all of the members of a zip archive into the given directory.

    :param zipfile: An instance of zipfile.ZipFile.
    :param dir_path: The path to the directory.

    :returns: None

    :raises RuntimeError: When the archive contains illegal paths (such as
        paths that may try to escape the directory). Nothing will be extracted
        in this case, all or nothing style.

    .. note::

        This function could be made quite a bit safer by implementig
        extractall() ourselves.

    """

    for i in zipfile.namelist():
        i = i.decode("ascii")

        if os.path.isabs(i):
            raise RuntimeError("absolute path found")

        if u".." in i:
            raise RuntimeError(".. found")

    zipfile.extractall(dir_path)

EXECUTE_BUFFER_SIZE = 4096
def execute(args, stdin_data, uid, gid, buffer_limit, timeout):
    def demote():
        os.setuid(uid)
        os.setgid(gid)

    process = subprocess.Popen(args, stdin = subprocess.PIPE,
        stdout = subprocess.PIPE, stderr = subprocess.PIPE,
        preexec_fn = demote, close_fds = True, cwd = os.path.dirname(args[0]))

    def set_non_blocking(f):
        # Grab the file status flags
        flags = fcntl.fcntl(f.fileno(), fcntl.F_GETFL)

        fcntl.fcntl(f.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

    # Make the process's output file handlers be non-blocking. This
    # won't affect the write end of the pipe. After this is done however, we
    # need to be sure to not use any of the high level file operations and
    # instead only read via os.read.
    set_non_blocking(process.stdout)
    set_non_blocking(process.stderr)

    process.stdin.write(stdin_data)
    process.stdin.close()

    # Figure out when the process needs to die by
    deadline = (datetime.datetime.today() +
        datetime.timedelta(seconds = timeout))

    # We're going to buffer stdin and stdout on the filesystem
    buffers = [tempfile.TemporaryFile(), tempfile.TemporaryFile()]
    buffers_nbytes = [0, 0]

    while process.poll() is None:
        # Figure out how long we have until our deadline
        time_to_wait = deadline - datetime.datetime.today()

        # Check if we're past our deadline by looking for a negative
        # timedelta.
        if time_to_wait.days < 0:
            break

        # Wait for the process to feed us input
        ready, _w, _e = select.select([process.stdout, process.stderr],
            [], [], time_to_wait.seconds)

        # If a timeout occurs
        if not ready:
            break

        # Read from stdout and stderr
        exceeded_buffer = False
        for k, v in enumerate([process.stdout, process.stderr]):
            # If there's data waiting in the buffer
            if v in ready:
                data = os.read(v.fileno(), EXECUTE_BUFFER_SIZE)
                buffers[k].write(data)
                buffers_nbytes[k] += len(data)

                if buffers_nbytes[k] > buffer_limit:
                    exceeded_buffer = True

        if exceeded_buffer:
            break

    # If the process is still alive, kill it
    if process.poll() is None:
        process.kill() # brutally murder the process
        process.wait()

    # We'll grab the remaining data in the pipes as long as we don't exceed our
    # maximum sizes.
    for k, v in enumerate([process.stdout, process.stderr]):
        try:
            while buffers_nbytes[k] < buffer_limit:
                data = os.read(v.fileno(), EXECUTE_BUFFER_SIZE)
                if data == "":
                    break

                buffers[k].write(data)
                buffers_nbytes[k] += len(data)
        except OSError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                pass
            else:
                raise

    for i in buffers:
        i.seek(0)

    return process.returncode, buffers[0], buffers[1]

def handle_message(msg, con):
    """
    Handles the the ``msg`` received from ``con`` (a UntrustedConnection
    object).

    """

    global config

    if msg.command == u"ping":
        return Message("pong", msg.payload)

    if msg.command == u"init":
        if config is not None:
            log.warning("Bootstrapper was initialized twice")
            return Message("error", u"already configured")

        decoded_payload = msg.payload.decode("utf_8")
        received_config = json.loads(decoded_payload)
        if set(received_config.keys()) != INIT_FIELDS:
            return Message("error", u"bad configuration")

        config = received_config

        return Message("ok", u"")

    if msg.command == u"auth":
        if config is None:
            return Message("error", u"no secret set yet")

        if msg.payload == config["secret"]:
            con.authenticated = True
            return Message("ok", "")
        else:
            log.warning("Failed auth from peer")
            return Message("error", u"bad secret")

    # Every command that follows needs the peer to be authenticated
    if config is None or not con.authenticated:
        return Message("error", u"you are not authenticated")

    if msg.command == u"get_config":
        serialized_config = json.dumps(config, ensure_ascii = False)
        return Message("config", serialized_config)

    if msg.command == u"provision":
        with tempfile.NamedTemporaryFile(delete = False) as f:
            temp_path = f.name
            f.write(msg.payload)

        # The tempfile module inits it to 600, we need to make it executable as
        # well.
        os.chmod(temp_path, 0700)

        p = subprocess.Popen([temp_path], stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
        output = p.communicate()[0]

        os.remove(temp_path)

        return Message("provision_output", output)

    if (msg.command == u"upload_harness" or
            msg.command == u"upload_submission"):
        # The primary different between the two commands is where it stores the
        # payload. We resolve that difference here.
        is_harness = msg.command == u"upload_harness"
        if is_harness:
            target_directory = config["harness_directory"]
        else:
            target_directory = config["submission_directory"]

        # This plays double duty of catching bad configurations and erroring
        # if the user uploads something twice.
        if len(os.listdir(target_directory)) > 0:
            return Message("error", u"target directory not empty")

        with tempfile.TemporaryFile() as f:
            f.write(msg.payload)
            f.seek(0)

            archive = zipfile.ZipFile(f, mode = "r")

            if is_harness and "main" not in archive.namelist():
                return Message("error", u"no main file in test harness")

            log.info("Extracting archive with members %r to %r",
                archive.namelist(), target_directory)

            try:
                safe_extraction(archive, target_directory)
            except RuntimeError as e:
                return Message("error", unicode(e))
            finally:
                archive.close()

        return Message("ok", "")

    if msg.command == "run_harness":
        decoded_payload = msg.payload.decode("utf_8")
        payload_dict = json.loads(decoded_payload)
        if set(payload_dict.keys()) != RUN_HARNESS_FIELDS:
            return Message("error", u"invalid payload")

        harness_executable = os.path.join(config["harness_directory"], "main")
        if not os.path.exists(harness_executable):
            return Message("error", u"no harness executable found")

        # Get the UID from the username if that was provided
        uid = config["user"]
        if isinstance(uid, basestring):
            uid = pwd.getpwname(uid).pw_uid

        # Same for the GID
        gid = config["group"]
        if isinstance(gid, basestring):
            gid = grp.getgrname(gid).gr_gid

        # Make sure the permissions of the harness directory and submission
        # directory are such that the testing user has ownership of them.
        for i in [config["harness_directory"], config["submission_directory"]]:
            os.chmod(i, 0700)
            os.chown(i, uid, gid)
            for root, dirnames, filenames in os.walk(i):
                for j in dirnames + filenames:
                    os.chmod(os.path.join(root, j), 0700)
                    os.chown(os.path.join(root, j), uid, gid)

        # Execute the harness and time how long it takes
        start_time = datetime.datetime.today()
        return_code, out, err = execute([harness_executable],
            payload_dict["harness_input"].encode("ascii"), uid, gid,
            payload_dict["buffer_limit"], payload_dict["timeout"])

        results = {
            "stdout": out.read(),
            "stderr": err.read(),
            "return_code": return_code,
            "total_time": (datetime.datetime.today() - start_time).seconds
        }

        # This should be done by the marshal library but I don't want to do a
        # bunch of magic to ensure that it gets into the VM as well.
        unencoded = json.dumps(results, separators = (",", ":"),
            ensure_ascii = False)

        return Message("results", unencoded.encode("utf_8"))

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
