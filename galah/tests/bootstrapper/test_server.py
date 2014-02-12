# internal
from galah.bootstrapper import protocol, server
from galah.common import marshal

# stdlib
import socket
import time
import tempfile
import shutil
import zipfile
import os

# external
import pytest

# Tell pytest to load our bootstrapper plugin. Absolute import is required here
# though I'm not sure why. It does not error when given simply "bootstrapper"
# but it does not correclty load the plugin.
pytest_plugins = ("galah.tests.bootstrapper.pytest_bootstrapper", )

# A crazy unicode string that renders as scribbles
UNICODE_TEST_SCRIBBLES = (
    u" \u031b \u0340 \u0341 \u0358 \u0321 \u0322 \u0327 \u0328 \u0334 \u0335 "
    u"\u0336 \u034f \u035c \u035d \u035e \u035f \u0360 \u0362 \u0338 \u0337 "
    u"\u0361 \u0489"
)

class TestLiveInstance:
    def test_flood(self, bootstrapper_server):
        """
        Tests handling of disconnects and reconnects by opening up multiple
        connections one after the other and sending pings through them.

        """

        for i in range(10):
            con = bootstrapper_server()

            for j in range(5):
                con.send(protocol.Message("ping", str(i)))
                message = con.recv()
                assert message.command == "pong"
                assert message.payload == str(i)

            con.shutdown()

    def test_multiple_connections(self, bootstrapper_server):
        """
        Tests whether the server can handle multiple connections at once.

        """

        # We create our connections here. If we do them immediately after
        # eachother the connect call (that is hidden from us at this layer)
        # fails with an EAGAIN error immediately despite Python's attempt to
        # give us timeouts instead. I assume this is because the server has
        # too many connections queued up waiting to be serviced and I don't
        # expect it to be a problem we'll ever see in production.
        connections = []
        for i in range(10):
            connections.append(bootstrapper_server())
            time.sleep(0.1)

        for k, i in enumerate(connections):
            i.send(protocol.Message("ping", str(k)))
            i.send(protocol.Message("ping", str(k)))

        for k, i in enumerate(connections):
            message = i.recv()
            assert message.command == "pong"
            assert message.payload == str(k)

            message2 = i.recv()
            assert message2.command == "pong"
            assert message2.payload == str(k)

            i.shutdown()

    def test_bad_message(self, bootstrapper_server):
        """
        Tests that the server sends an error response when given an invalid
        command and disconnects, but stays alive.

        """

        con = bootstrapper_server()
        con.send(protocol.Message("not_a_command", "some data"))
        message = con.recv()
        assert message.command == "error"
        con.send(protocol.Message("ping", "data"))
        with pytest.raises(socket.timeout):
            con.recv()
        con.shutdown()

        con = bootstrapper_server()
        con.send(protocol.Message("ping", "data"))
        message2 = con.recv()
        assert message2.command == "pong"
        assert message2.payload == "data"
        con.shutdown()

    def test_ping(self, bootstrapper_server):
        """
        Basic test ensuring the bootstrapper server responds to pings.

        """

        con = bootstrapper_server()

        ping_message = protocol.Message("ping", "data")
        con.send(ping_message)

        msg = con.recv()
        assert msg.command == "pong"
        assert msg.payload == ping_message.payload

    def test_init_auth(self, bootstrapper_server):
        """
        Tests that the init command works, as well as the auth command.

        """

        secret = "very secret"
        test_config = {
            "user": 100,
            "group": 100,
            "harness_directory": "/tmp/harness",
            "submission_directory": UNICODE_TEST_SCRIBBLES,
            "secret": secret
        }
        test_config_serialized = marshal.dumps(test_config)

        # Create a bad configuration by adding a bogus key
        bad_test_config = dict(test_config.items() + [("bla", "bla")])
        bad_test_config_serialized = marshal.dumps(bad_test_config)

        con = bootstrapper_server()
        con.send(protocol.Message("init", bad_test_config_serialized))
        msg = con.recv()
        assert msg.command == "error"

        # The server will close our connection on error so open another
        con = bootstrapper_server()
        con.send(protocol.Message("init", test_config_serialized))
        msg = con.recv()
        assert msg.command == "ok"

        # We now need to auth in order to get the configuration
        con.send(protocol.Message("auth", secret))
        msg = con.recv()
        assert msg.command == "ok"

        con.send(protocol.Message("get_config", ""))
        msg = con.recv()
        assert msg.command == "config"
        assert marshal.loads(msg.payload) == test_config

        con.shutdown()

    def test_provision(self, bootstrapper_server):
        """Tests that the provision command works as expected."""

        expected_output = "Good day sir"
        test_script = """#!/usr/bin/env bash
        echo "%s"
        """ % (expected_output, )

        # The output of the script will actually contain a trailing newline
        expected_output += "\n"

        con = bootstrapper_server()

        secret = "super secret"
        test_config = {
            "user": "notvalid",
            "group": "notvalid",
            "harness_directory": "/dev/null",
            "submission_directory": "/dev/null",
            "secret": secret
        }
        con.send(protocol.Message("init", marshal.dumps(test_config)))
        assert con.recv().command == "ok"
        con.send(protocol.Message("auth", secret))
        assert con.recv().command == "ok"

        con.send(protocol.Message("provision", test_script))
        msg = con.recv()
        assert msg.command == "provision_output"
        assert msg.payload == expected_output
        con.shutdown()

    TEST_ARCHIVES = [
        {
            "files": {
                "../file.test": "Delicious applesauce",
                "a/file.test": "Even more delicious applesauce",
                "a/unicode": UNICODE_TEST_SCRIBBLES.encode("utf_8")
            },
            "type": "submission",
            "should_succeed": False
        },
        {
            "files": {
                "main": "lalalala",
                "../file.test": "Delicious applesauce",
                "a/file.test": "Even more delicious applesauce",
                "a/unicode": UNICODE_TEST_SCRIBBLES.encode("utf_8")
            },
            "type": "submission",
            "should_succeed": False
        },
        {
            "files": {
                "main": "lalala",
                "file.test": "Delicious applesauce",
                "a/file.test": "Even more delicious applesauce",
                "a/unicode": UNICODE_TEST_SCRIBBLES.encode("utf_8")
            },
            "type": "submission",
            "should_succeed": True
        },
        {
            "files": {
                "main": "lalala",
                "file.test": "Delicious applesauce",
                "a/file.test": "Even more delicious applesauce",
                "a/unicode": UNICODE_TEST_SCRIBBLES.encode("utf_8")
            },
            "type": "harness",
            "should_succeed": True
        },
        {
            "files": {
                "file.test": "Delicious applesauce",
                "a/file.test": "Even more delicious applesauce",
                "a/unicode": UNICODE_TEST_SCRIBBLES.encode("utf_8")
            },
            "type": "harness",
            "should_succeed": False
        }
    ]

    @pytest.mark.parametrize("archive_info", TEST_ARCHIVES)
    def test_upload(self, bootstrapper_server, archive_info):
        """
        Tests the upload_harness and upload_submission commands.

        """

        # We will get the bootstrapper to unpack the archive here
        temp_dir = tempfile.mkdtemp()

        try:
            con = bootstrapper_server()

            # Initialize the bootstrapper
            is_harness = archive_info["type"] == "harness"
            secret = "super secret"
            test_config = {
                "user": "notvalid",
                "group": "notvalid",
                "harness_directory": temp_dir if is_harness else "/dev/null",
                "submission_directory":
                    temp_dir if not is_harness else "/dev/null",
                "secret": secret
            }
            con.send(protocol.Message("init", marshal.dumps(test_config)))
            assert con.recv().command == "ok"
            con.send(protocol.Message("auth", secret))
            assert con.recv().command == "ok"

            # Create the test archive and send it to the bootstrapper
            with tempfile.TemporaryFile() as f:
                test_zipfile = zipfile.ZipFile(f, mode = "w")
                for k, v in archive_info["files"].items():
                    test_zipfile.writestr(k, v)
                test_zipfile.close()

                f.seek(0)

                command = ("upload_harness" if is_harness else
                    "upload_submission")
                con.send(protocol.Message(command, f.read()))

            if archive_info["should_succeed"]:
                # Print everything in the temp directory for the debugger's
                # sake.
                print repr(list(os.walk(temp_dir)))

                assert con.recv().command == "ok"

                for k, v in archive_info["files"].items():
                    adjusted_path = os.path.join(temp_dir, k)
                    assert os.path.isfile(adjusted_path)
                    assert open(adjusted_path, "rb").read() == v
            else:
                assert con.recv().command == "error"

            con.shutdown()
        finally:
            # Make sure we don't leave a bunch of temporary directories lying
            # around after testing.
            shutil.rmtree(temp_dir)

    def test_auth(self, bootstrapper_server):
        con = bootstrapper_server()
        secret = "super secret"
        test_config = {
            "user": "notvalid",
            "group": "notvalid",
            "harness_directory": "/dev/null",
            "submission_directory": "/dev/null",
            "secret": secret
        }
        con.send(protocol.Message("init", marshal.dumps(test_config)))
        assert con.recv().command == "ok"
        con.shutdown()

        con = bootstrapper_server()
        con.send(protocol.Message("get_config", ""))
        assert con.recv().command == "error"
        con.shutdown()

        con = bootstrapper_server()
        con.send(protocol.Message("auth", secret + "not correct"))
        assert con.recv().command == "error"
        con.shutdown()

        con = bootstrapper_server()
        con.send(protocol.Message("auth", secret))
        assert con.recv().command == "ok"
        con.send(protocol.Message("get_config", ""))
        assert con.recv().command == "config"
        con.shutdown()
