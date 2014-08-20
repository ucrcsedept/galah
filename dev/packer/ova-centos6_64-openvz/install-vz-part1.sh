#!/usr/bin/env bash

# This will ensure that the script exits if a failure occurs
set -e

# This will echo every line
set -x

cat > /etc/yum.repos.d/openvz.repo <<EOF
[openvz-utils]
name=OpenVZ user-space utilities
#baseurl=http://download.openvz.org/current/
mirrorlist=http://download.openvz.org/mirrors-current
enabled=1
gpgcheck=1
gpgkey=http://download.openvz.org/RPM-GPG-Key-OpenVZ

[openvz-kernel-rhel6]
name=OpenVZ RHEL6-based stable kernels
#baseurl=http://download.openvz.org/kernel/branches/rhel6-2.6.32/current/
mirrorlist=http://download.openvz.org/kernel/mirrors-rhel6-2.6.32
enabled=1
gpgcheck=1
gpgkey=http://download.openvz.org/RPM-GPG-Key-OpenVZ
exclude=vzkernel-firmware
EOF

chown root:root /etc/yum.repos.d/openvz.repo
chmod 644 /etc/yum.repos.d/openvz.repo

yum -y install vzkernel vzctl vzquota ploop

/sbin/shutdown -r now

# This is so packer doesn't start on the next script until we restart
sleep 60
