# Expand variables and fail on first error
set -e
set -x

# Install dependencies
rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum -y install perl dkms gcc kernel-headers-$(uname -r) kernel-devel-$(uname -r)

# Just in case guest additions writes anything to the current directory, we'll
# change into /tmp
cd /tmp

# Mount the ISO
MOUNT_POINT=$(mktemp -d)
mount -o loop /root/VBoxGuestAdditions.iso $MOUNT_POINT

# Install guest additions
bash $MOUNT_POINT/VBoxLinuxAdditions.run || true

# Unmount the ISO
umount $MOUNT_POINT

# Clean up
rm -f /root/VBoxGuestAdditions.iso
rmdir $MOUNT_POINT
