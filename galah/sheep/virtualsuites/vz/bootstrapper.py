#!/usr/bin/env python

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