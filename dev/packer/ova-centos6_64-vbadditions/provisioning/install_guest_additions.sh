# Expand variables and fail on first error
set -e
set -x

cd /tmp

# Download the virtualbox
yum -y install wget
wget http://download.virtualbox.org/virtualbox/LATEST.TXT
VBOX_VERSION=$(cat LATEST.TXT | tr -d " ")
wget http://download.virtualbox.org/virtualbox/$VBOX_VERSION/VBoxGuestAdditions_${VBOX_VERSION}.iso

# Install dependencies
yum -y remove kernel-headers kernel-devel vzkernel-headers vzkernel-devel
if [[ $(uname -r) == *stab* ]]; then
    yum -y install vzkernel-headers-$(uname -r) vzkernel-devel-$(uname -r)
else
    yum -y install kernel-headers-$(uname -r) kernel-devel-$(uname -r)
fi
yum -y install perl gcc

# Mount the ISO
MOUNT_POINT=$(mktemp -d)
mount -o loop VBoxGuestAdditions_${VBOX_VERSION}.iso $MOUNT_POINT

# Install guest additions
bash $MOUNT_POINT/VBoxLinuxAdditions.run || true

# Unmount the ISO
umount $MOUNT_POINT

# Clean up
rm -f VBoxGuestAdditions_${VBOX_VERSION}.iso
rmdir $MOUNT_POINT
