# internal
from galah.bootstrapper import protocol, server

# external
import pytest

# stdlib
import itertools
import socket
import sys
import os.path
import inspect
import subprocess
import tempfile
import time
import signal
import shutil

# A crazy unicode string suitable for use in testing. Prints as
# "THE PONY HE COMES" with tons of decoration.
UNICODE_TEST_PONY = (
    u"TH\u0318E\u0344\u0309\u0356 \u0360P\u032f\u034d\u032dO\u031a\u200bN"
    u"\u0310Y\u0321 H\u0368\u034a\u033d\u0305\u033e\u030e\u0321\u0338\u032a"
    u"\u032fE\u033e\u035b\u036a\u0344\u0300\u0301\u0327\u0358\u032c\u0329 "
    u"\u0367\u033e\u036c\u0327\u0336\u0328\u0331\u0339\u032d\u032fC\u036d"
    u"\u030f\u0365\u036e\u035f\u0337\u0319\u0332\u031d\u0356O\u036e\u034f"
    u"\u032e\u032a\u031d\u034dM\u034a\u0312\u031a\u036a\u0369\u036c\u031a"
    u"\u035c\u0332\u0316E\u0311\u0369\u034c\u035d\u0334\u031f\u031f\u0359"
    u"\u031eS\u036f\u033f\u0314\u0328\u0340\u0325\u0345\u032b\u034e\u032d"
)

TEST_MESSAGES = [
    protocol.Message(command = "test", payload = UNICODE_TEST_PONY),
    protocol.Message(command = "test2", payload = "test payload"),
    protocol.Message(command = "", payload = ""),
    protocol.Message(command = "empty_payload", payload = "")
]

@pytest.mark.parametrize("test_message", TEST_MESSAGES)
def test_single_encode_decode(test_message):
    """
    Tests that all of the test messages can be encoded and decoded properly by
    the protocol module. Each message is tested individually with its own
    fresh decoder instance.

    """

    encoded_message = protocol.serialize(test_message)
    print "Encoded Message:", repr(encoded_message)

    decoder = protocol.Decoder()

    # Feed the decoder every character except the last, it should not be able
    # to decode a complete message during that time.
    for i in encoded_message[:-1]:
        decoded_message = decoder.decode(i)
        assert decoded_message is None

    # The decoder should be able to complete the message with the last
    # character.
    decoded_message = decoder.decode(encoded_message[-1])
    assert decoded_message is not None

    assert decoded_message.command == test_message.command

    if isinstance(test_message.payload, unicode):
        decoded_message.payload = \
            decoded_message.payload.decode("utf_8")
    assert decoded_message.payload == test_message.payload

def test_stream():
    """
    Tests that a stream of messages are all encoded and decoded properly.

    """

    # This will create a flat list of messages containing every possible
    # ordering of our list of test messages.
    combos = itertools.combinations(TEST_MESSAGES, len(TEST_MESSAGES))
    message_stream = [i for combo in combos for i in combo]

    decoder = protocol.Decoder()
    for i in message_stream:
        print "Decoding Message:", repr(i)
        encoded_message = protocol.serialize(i)
        print "Encoded Message:", repr(encoded_message)

        # Feed the decoder every character except the last, it should not be
        # able to decode a complete message during that time.
        for j in encoded_message[:-1]:
            decoded_message = decoder.decode(j)
            assert decoded_message is None

        # The decoder should be able to complete the message with the last
        # character.
        decoded_message = decoder.decode(encoded_message[-1])
        assert decoded_message is not None

        assert decoded_message.command == i.command

        if isinstance(i.payload, unicode):
            decoded_message.payload = \
                decoded_message.payload.decode("utf_8")
        assert decoded_message.payload == i.payload

@pytest.fixture
def bootstrapper_server(request):
    # Create a temporary directory that will house our unix socket
    temp_dir = tempfile.mkdtemp()
    socket_path = os.path.join(temp_dir, "bootstrapper-socket")

    # This will execute the server with the interpreter that is executing this
    # code. Output will go to our standard error
    args = [sys.executable, inspect.getsourcefile(server), "--log-dir",
        temp_dir,"--uds", socket_path]
    server_process = subprocess.Popen(args, stdout = sys.stderr,
        stderr = subprocess.STDOUT)

    def cleanup():
        # Brutally murder the server process
        os.kill(server_process.pid, signal.SIGKILL)

        # Delete the temporary directory
        shutil.rmtree(temp_dir)
    request.addfinalizer(cleanup)

    # Wait for the server to start up and create the socket file
    tries_left = 5
    while not os.path.exists(socket_path):
        time.sleep(.3)

        tries_left -= 1
        if tries_left <= 0:
            pytest.fail("Could not start bootstrapper server.")

    # Connect to the bootstrapper
    bootstrapper_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    bootstrapper_sock.settimeout(4)
    bootstrapper_sock.connect(socket_path)

    return protocol.Connection(bootstrapper_sock)

class TestLiveInstance:
    def test_ping(self, bootstrapper_server):
        ping_message = protocol.Message("ping", "data")
        bootstrapper_server.send(ping_message)

        received_messages = bootstrapper_server.recv()
        assert len(received_messages) == 1
        assert received_messages[0].command == "pong"
        assert received_messages[0].payload == ping_message.payload
