# Just in case guest additions writes anything to the current directory, we'll
# change into /tmp
cd /tmp

# Mount the ISO
MOUNT_POINT=$(mktemp -d)
mount -o loop /root/VBoxGuestAdditions.iso $MOUNT_POINT

# Install guest additions
bash $MOUNT_POINT/VBoxLinuxAdditions.run

# Unmount the ISO
umount $MOUNT_POINT

# Clean up
rm -f /root/VBoxGuestAdditions.iso
rmdir $MOUNT_POINT
