#!/usr/bin/env bash

# This will ensure that the script exits if a failure occurs
set -e

# This will echo every line
set -x

# C++ is required for PyZMQ (one of Galah's dependencies)
yum -y install python-virtualenv zeromq gcc-c++ git

virtualenv /tmp/galah-venv
/tmp/galah-venv/bin/pip install /opt/galah || true
/tmp/galah-venv/bin/pip uninstall galah || true
chown -R vagrant:vagrant /tmp/galah-venv

mkdir -p /etc/galah
cat > /etc/galah/galah.config <<EOF
config = {}

config["web/DEBUG"] = True
config["web/SECRET_KEY"] = "asldfhlaskdjf"
config["web/HOST_URL"] = "http://localhost:5000"

import logging
logger_galah = logging.getLogger("galah")
logger_galah.setLevel(logging.DEBUG)

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(logging.Formatter(
    "[%(levelname)s;%(name)s;%(lineno)s]: %(message)s"
))
logger_galah.addHandler(streamhandler)
EOF

cat > /tmp/ready-galah.sh <<EOF
alias d="cd"
alias s="ls"
source /tmp/galah-venv/bin/activate
export PYTHONPATH=/opt/galah
cd /opt/galah/galah
EOF
