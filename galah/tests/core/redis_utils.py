# stdlib
import re
import socket
import sys
import threading
import StringIO
import collections

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

        self._sock = socket.create_connection((host, port))
        self._sock.sendall("MONITOR\n")

        self._alive = True # Flag for thread to keep going
        self._thread = threading.Thread(target = self._monitor_thread_main)
        self._thread.start()

    def stop(self, dump_buffer = True, join = True):
        self._alive = False
        self._thread.join()

        if dump_buffer:
            print "--- Dumping Redis MONITOR Output ---"
            self._output_buffer.seek(0)
            for i in self._output_buffer:
                print i

    def _monitor_thread_main(self):
        # A regex that can pull out the DB number form a line of output from
        # MONITOR. An example line is
        # `+1339518083.107412 [0 127.0.0.1:60866] "keys" "*"` where that 0 is
        # the DB number.
        DB_NUMBER_RE = re.compile(r"[\d\s+.]+\[(?P<db>\d+) [^ :]+:\d+\]")

        # Terminal effect codes
        EFFECT_FAINT = "\x1b[2m" if self.effects else ""
        EFFECT_RESET = "\x1b[0m" if self.effects else ""

        buf = [""]
        while self._alive:
            # Ensure that we never block for much more than 0.1 seconds
            self._sock.settimeout(0.1)

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
                parsed_line = DB_NUMBER_RE.match(line)
                if parsed_line is None or \
                        int(parsed_line.group("db")) != self.db:
                    self._output_buffer.write(EFFECT_FAINT + line +
                        EFFECT_RESET + "\n")
                else: # this line is about the selected database
                    self._output_buffer.write(line + "\n")

            self._output_buffer.flush()
            buf = [buf[-1]]
