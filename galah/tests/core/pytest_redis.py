# stdlib
import re
import socket
import sys
import threading
import StringIO
import collections
import inspect

# external
import pytest
import redis

def pytest_runtest_setup(item):
    using_redis = "redis_server" in inspect.getargspec(item.function).args
    if using_redis:
        raw_config = item.config.getoption("--redis")
        if not raw_config:
            pytest.skip("Configuration with `--redis` required for this test.")
        config = parse_redis_config(raw_config)

        # Start the Redis monitor so we can see what commands get run.
        monitor = RedisMonitor(host = config.host, port = config.port,
            db = config.db_range[0])

        item._redis_monitor = monitor

        # This will make sure that the monitor thread is stopped no matter
        # what happens (supposedly at least).
        item.addfinalizer(lambda: monitor.stop())

# Best explained at http://stackoverflow.com/a/10806465/1989056
@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    rep = __multicall__.execute()

    if call.when == "call":
        rep.sections.append(
            ("Redis MONITOR Output", item._redis_monitor.stop()))

    return rep

@pytest.fixture
def redis_server(request):
    raw_config = request.config.getoption("--redis")
    if not raw_config:
        pytest.skip("Configuration with `--redis` required for this test.")
    config = parse_redis_config(raw_config)

    db = config.db_range[0]
    connection = redis.StrictRedis(host = config.host, port = config.port,
        db = db)

    # This will delete everything in the current database
    connection.flushdb()

    return connection

RedisConfig = collections.namedtuple("RedisConfig",
    ["host", "port", "db_range"])

def parse_redis_config(raw):
    # Parse the configuration string
    REDIS_CONFIG_RE = re.compile(r"(?P<host>[^:]+):(?P<port>[0-9]+):"
        r"(?P<db_start>[0-9]+)\-(?P<db_end>[0-9]+)")
    config = REDIS_CONFIG_RE.match(raw)
    if config is None:
        pytest.fail("Invalid --redis configuration.")

    return RedisConfig(
        host = config.group("host"),
        port = int(config.group("port")),
        db_range = range(
            int(config.group("db_start")),
            int(config.group("db_end")) + 1
        )
    )

class RedisMonitor:
    """
    This class will connect to the specified Redis instance and write any
    commands it receives to the given file (stdout by default).

    :ivar host: The host serving the Redis server.
    :ivar port: The port to access the Redis server on.
    :ivar db: The database number we're most interested in. Commands sent to
        other databases will be grayed out if effects are enabled.
    :ivar out: The file-like object to write the commands to.
    :ivar effects: Whether or not to use terminal colors (see the description
        for the db instance variable).

    .. warning::

        Do not change any of the instance variables after instantiation. I
        didn't bother going to lengths to make them read-only. The reason for
        this is that a thread is spun off who then accesses the instance
        often to figure out what its supposed to do.

    """

    def __init__(self, host, port, db = 0, effects = True):
        self.host = host
        self.port = port
        self.db = db
        self.effects = effects

        self._output_buffer = StringIO.StringIO()

        # We'll wait 10 seconds for Redis to accept our connection
        self._sock = socket.create_connection((host, port), 10)
        self._sock.settimeout(0.1) # 0.1 seconds timeout on blocking ops

        # Tell Redis we want to monitor all commands.
        self._sock.sendall("MONITOR\n")

        # Wait until we get an OK. We'll try to read from the socket 10
        # times to give Redis some time to send the OK.
        OK = "+OK"
        data = ""
        for i in range(10):
            try:
                data += self._sock.recv(len(OK) - len(data))
                if len(data) == len(OK):
                    break
            except socket.timeout:
                pass
        else:
            raise RuntimeError("Did not receive response from Redis.")
        if data != OK:
            # Grab whatever else has been sent so we can provide a useful
            # error message.
            data += self._sock.recv(2024)

            raise RuntimeError("Redis returned a non-OK status. Redis sent: %s"
                % (repr(data), ))

        self._alive = True # Flag for thread to keep going
        self._thread = threading.Thread(target = self._monitor_thread_main)
        self._thread.daemon = True
        self._thread.start()

    def stop(self, join = True):
        self._alive = False
        self._thread.join()

        return self._output_buffer.getvalue()

    def _monitor_thread_main(self):
        # A regex that can pull out the DB number form a line of output from
        # MONITOR. An example line is
        # `+1339518083.107412 [0 127.0.0.1:60866] "keys" "*"` where that 0 is
        # the DB number.
        DB_NUMBER_RE = re.compile(r"[\d\s+.]+\[(?P<db>\d+) ([^ :]+:\d+|lua)\]")

        # Terminal effect codes
        EFFECT_FAINT = "\x1b[2m" if self.effects else ""
        EFFECT_RESET = "\x1b[0m" if self.effects else ""

        buf = [""]
        while self._alive:
            try:
                # Grab data off the wire
                data = self._sock.recv(2048)

                # Split the data on CRLF (which is how Redis delimits lines)
                split_data = data.split("\r\n")

                # The first item in the split data belongs with the last line
                buf[-1] += split_data[0]

                # The rest of the items are there own lines and should be
                # given their own slots in the buf list.
                buf += split_data[1:]
            except socket.timeout:
                pass

            # Handle every line except for the last one which is still being
            # built.
            for line in buf[0:-1]:
                # Ignore any blank lines that manage to sneak in
                if len(line.strip()) == 0:
                    continue

                parsed_line = DB_NUMBER_RE.match(line)
                if parsed_line is None or \
                        int(parsed_line.group("db")) != self.db:
                    self._output_buffer.write(EFFECT_FAINT + line +
                        EFFECT_RESET + "\n")
                else: # this line is about the selected database
                    self._output_buffer.write(line + "\n")

            self._output_buffer.flush()
            buf = [buf[-1]]
