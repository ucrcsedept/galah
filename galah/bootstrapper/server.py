class BaseState(object):


class Server(object):
    states = set(u"NOT_READY", u"IDLE", u"HARNESS_READY", u"TEST_READY",
       u"RUNNING_TEST", u"RESULTS_READY")

    commands = set(u"init")

    def __init__(self):
        self.state = states

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        assert isinstance(value, unicode) and value in states, \
            "invalid state: %r" % (value, )

        self._state = value

    def handle_command(self, command, payload):
        func = getattr(self, "handle_%s" % (command.encode("ascii"), ), None)
        if fun is None:
            raise ValueError("command %r not found" % (command, ))

    @command
    def handle_
