#!/usr/bin/env python

# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

import socket
import sys
import json
import subprocess
import os
import os.path

# Bind to a good ole' fashioned tcp socket.
sheep_listener = \
    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sheep_listener.bind(("0.0.0.0", 6668))
sheep_listener.setblocking(1)
sheep_listener.listen(1)

# Wait for the sheep to connect to us.
print >> sys.stderr, "[bootstrapper] Waiting for sheep to connect."
try:
    sheep, sheep_address = \
        sheep_listener.accept()
except socket.timeout:
    exit(1)

# We're going to treat the socket just like a file object.
sheep_fd = sheep.makefile()

# We're guarenteed that the entire test request is contained on a single line.
print >> sys.stderr, "[bootstrapper] Waiting for test request."
test_request = sheep_fd.readline()
print >> sys.stderr, "[bootstrapper] Received test request", test_request
test_request = json.loads(test_request)

# Demote ourselves
os.setgid(test_request["vz/gid"])
os.setuid(test_request["vz/uid"])

# Start the test harness
print >> sys.stderr, "[bootstrapper] Starting test harness."
harness = subprocess.Popen(
	os.path.join(test_request["harness_directory"], "main"),
	stdin = subprocess.PIPE,
	stdout = sheep_fd,
	stderr = subprocess.STDOUT
)
harness.stdin.write(json.dumps(test_request))
harness.stdin.close()
harness.wait()

sheep_fd.close()
sheep.close()

exit(harness.returncode)
