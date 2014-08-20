#!/usr/bin/env bash

# This will ensure that the script exits if a failure occurs
set -e

# This will echo every line
set -x

useradd vagrant -m

# Create bagrant user's `.ssh/` directory
mkdir /home/vagrant/.ssh/
chown vagrant:vagrant /home/vagrant/.ssh
chmod 700 /home/vagrant/.ssh

# Add insecure vagrant public key
cat > /home/vagrant/.ssh/authorized_keys <<EOF
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key
EOF

chown vagrant:vagrant /home/vagrant/.ssh/authorized_keys
chmod 600 /home/vagrant/.ssh/authorized_keys

# Install sudo
yum install sudo

# Add vagrant user to sudoers
echo 'vagrant ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
echo 'Defaults:vagrant !requiretty' >> /etc/sudoers
visudo -cf /etc/sudoers
