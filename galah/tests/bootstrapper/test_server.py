# internal
from galah.bootstrapper import protocol, server

# stdlib
import socket

# external
import pytest

# Tell pytest to load our bootstrapper plugin. Absolute import is required here
# though I'm not sure why. It does not error when given simply "bootstrapper"
# but it does not correclty load the plugin.
pytest_plugins = ("galah.tests.bootstrapper.pytest_bootstrapper", )


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

    def test_bad_message(self, bootstrapper_server):
        """
        Tests that the server send an error response when given an invalid
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
