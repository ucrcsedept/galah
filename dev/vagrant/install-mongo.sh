#!/usr/bin/env bash

# This will ensure that the script exits if a failure occurs
set -e

# This will echo every line
set -x

# Install 10gen yum repo
cat > /etc/yum.repos.d/mongodb.repo <<EOF
[mongodb]
name=MongoDB Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
gpgcheck=0
enabled=1
EOF

chown root:root /etc/yum.repos.d/mongodb.repo
chmod 644 /etc/yum.repos.d/mongodb.repo

# Install latest MongoDB server
yum -y install mongo-10gen-server mongo-10gen

# Configure mongo
cat > /etc/mongod.conf <<EOF
# This configuration is only appropriate for use in development.

# Listen on an INET socket only
bind_ip = 127.0.0.1
port = 27017
nounixsocket = true

# Run in daemon mode and set sensible defaults. Don't change the pidfilepath
# or logpath options without also changing them within the mongod init file.
fork = true
pidfilepath = /tmp/mongodb.pid
logpath = /var/log/mongodb/mongod.log
dbpath = /data/db

# We don't care very much about durability because this is a configuration
# meant to be used only for development.
journal = false

# Disable the HTTP interface (Defaults to port+1000)
nohttpinterface = true

# Get MongoDB to only use a small amount of disk space
noprealloc = true
smallfiles = true
EOF

chown root:root /etc/mongod.conf
chmod 644 /etc/mongod.conf

# Where mongo will store its database
mkdir -p /data/db
chown mongod:mongod /data/db

# Restart mongo
service mongod restart
