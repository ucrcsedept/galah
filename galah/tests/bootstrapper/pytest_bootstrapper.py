# internal
from galah.bootstrapper import server, protocol

# external
import pytest

# stdlib
import subprocess
import time
import shutil
import os
import sys
import codecs
import tempfile
import inspect
import signal
import socket

@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    rep = __multicall__.execute()

    if call.when == "call" and "bootstrapper_server" in item.fixturenames:
        # Brutally murder the server process. We need it to be dead, otherwise
        # the read that follows will block forever.
        os.kill(item._bootstrapper_server_process.pid, signal.SIGKILL)

        server_output = item._bootstrapper_server_process.stdout.read()
        if len(server_output) > 0:
            rep.sections.append(("bootstrapper-server output", server_output))

        log_files = [i for i in os.listdir(item._bootstrapper_log_dir)
            if "log" in i]
        if len(log_files) == 1:
            rep.sections.append((
                "bootstrapper-server logs",
                codecs.open(os.path.join(item._bootstrapper_log_dir,
                    log_files[0]), "r", "utf_8").read()
            ))
        elif log_files > 1:
            raise RuntimeError("too many log files: %r" % (log_files, ))

    return rep

@pytest.fixture
def bootstrapper_server(request):
    """
    pytest fixture that will start up a bootstrapper server and give you access
    to it. The fixture's return value is a function that can be called with no
    arguments and it will return a new protocol.Connection object that is
    already connected to the server.

    """

    # Create a temporary directory that will house our unix socket
    temp_dir = tempfile.mkdtemp()
    socket_path = os.path.join(temp_dir, "bootstrapper-socket")

    # This will execute the server with the interpreter that is executing this
    # code. Output will go to our standard error
    args = [sys.executable, inspect.getsourcefile(server), "--log-dir",
        temp_dir,"--uds", socket_path]
    server_process = subprocess.Popen(args, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)

    # These will be used by our make report function to add proper sections to
    # our results.
    request.node._bootstrapper_server_process = server_process
    request.node._bootstrapper_log_dir = temp_dir

    # Ensure that the process and files are cleaned up once the test is done
    def cleanup():
        # Brutally murder the server process
        os.kill(server_process.pid, signal.SIGKILL)

        # Delete the temporary directory
        shutil.rmtree(temp_dir, ignore_errors = True)
    request.addfinalizer(cleanup)

    # Wait for the server to start up and create the socket file
    tries_left = 5
    while not os.path.exists(socket_path):
        time.sleep(.3)

        tries_left -= 1
        if tries_left <= 0:
            pytest.fail("Could not start bootstrapper server.")

    # Connect to the bootstrapper
    def create_connection():
        bootstrapper_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        bootstrapper_sock.settimeout(4)
        bootstrapper_sock.connect(socket_path)

        return protocol.Connection(bootstrapper_sock)

    return create_connection
