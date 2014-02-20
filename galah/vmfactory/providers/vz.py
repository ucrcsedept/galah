# stdlib
import subprocess
import os
import random
import shutil
import socket
import time
from datetime import datetime, timedelta

# internal
from .base import BaseProvider
import galah.bootstrapper
from galah.bootstrapper import protocol
from galah.common import marshal

import logging
log = logging.getLogger("galah.vmfactory")

from galah.base.config import load_config
config = load_config("")

NULL_FILE = open(os.devnull, "w")

class OpenVZProvider(BaseProvider):
    container_description = "galah-created"

    def __init__(self, test_config = None):
        self.vzctl_path = config["vmfactory/vz/VZCTL_PATH"]
        self.vzlist_path = config["vmfactory/vz/VZLIST_PATH"]
        self.id_range = config["vmfactory/vz/ID_RANGE"]
        self.allocate_ip = config["vmfactory/vz/ALLOCATE_IP"]
        self.os_template = config["vmfactory/vz/OS_TEMPLATE"]
        self.container_directory = config["vmfactory/vz/CONTAINER_DIRECTORY"]
        self.bootstrapper_directory = \
            config["vmfactory/vz/BOOTSTRAPPER_DIRECTORY"]
        self.guest_user = config["vmfactory/GUEST_USER"]
        self.guest_group = config["vmfactory/GUEST_GROUP"]
        self.submission_directory = config["vmfactory/SUBMISSION_DIRECTORY"]
        self.harness_directory = config["vmfactory/HARNESS_DIRECTORY"]

    def _run_vzctl(self, arguments):
        """
        Executes the ``vzctl`` utility with the given arguments.

        :param arguments: A list of arguments to pass to ``vzctl``.

        :returns: None

        :raises subprocess.CalledProcessError: If ``vzctl`` gave a non-zero
            return code.

        """

        cmd = [self.vzctl_path] + arguments

        # Return code of vzctl if the container is locked by another instance
        # of vzctl. See http://openvz.org/Man/vzctl.8#EXIT_STATUS
        CONTAINER_LOCKED = 9

        # We'll always retry for some time if we get a CONTAINER_LOCKED return
        # value from vzctl. This isn't configurable because I don't foresee
        # anyone ever needing to change it, also an easy change if someone says
        # they do.
        deadline = datetime.today() + timedelta(seconds = 20)

        while True:
            try:
                return subprocess.check_call(cmd, stdout = NULL_FILE,
                    stderr = NULL_FILE)
            except subprocess.CalledProcessError as e:
                if e.returncode == CONTAINER_LOCKED and \
                        datetime.datetime.today() < deadline:
                    # Just try again
                    continue
                else:
                    # Any other error should be allowed to propagate
                    raise

    def _execute(self, container, command):
        """
        Executes the given command in the container's default shell as the
        root user.

        :param container: The container ID.
        :param command: The command to run. This string will be passed to the
            default shell for the root user of the container (as far as I can
            tell, see vzctl's man page for more info).

        :returns: None

        :raises subprocess.CalledProcessError: If a non-zero exit status is
            returned by the command.

        """

        # We don't use our _run_vzctl function here because the return values
        # are not going to be what it expects.
        cmd = [self.vzctl_path, "exec2", container, command]
        subprocess.check_call(cmd, stdout = NULL_FILE, stderr = NULL_FILE)

    def _inject_file(self, container, source_path, dest_path):
        """
        Injects a file from the host system into the filesystem of the
        given container.

        The owner of the files will be the root user on the VM and the
        permissions will be set to 500 (read and execute by owner only).

        :param container: The container ID to inject the file into.
        :param source_path: The path to the file on the host system.
        :param dest_path: The path on the guest to copy the file to. Should be
            a full target path (ie: not a directory).

        """

        # Figure out the path on the host system of the dest_path (remember
        # that the guest filesystem is visible to us)
        if dest_path[0] != "/":
            raise ValueError("dest_path must be an absolute path")
        real_dest_path = os.path.join(self.container_directory, container,
            dest_path[1:])

        # Do the actual copy
        shutil.copyfile(source_path, real_dest_path)

        # Ensure that the permissions are set correctly (read and execute only
        # by owner) and owned by the root user
        self._execute(container, "chown root:root %s" % (dest_path, ))
        self._execute(container, "chmod 500 %s" % (dest_path, ))

    def _get_containers(self, galah_created):
        """
        Returns a list all existing containers.

        :param galah_created: If True, only containers created by Galah will
            be returned, otherwise all containers will be returned.

        :returns: A list of integers.

        """

        cmd = [self.vzlist_path, "--all", "--no-header", "--output", "ctid"]
        if galah_created:
            cmd += ["--description", self.container_description]

        # check_output would be better here but it's not supported in
        # Python 2.6
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
            stderr = NULL_FILE)
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise subprocess.CalledProcessError(returncode = p.returncode,
                cmd = cmd)

        return [int(i.strip()) for i in stdout.splitlines()]

    def create_vm(self):
        """
        Creates a new OpenVZ container.

        :returns: The metadata that should be associated with the VM as a
            dictionary.

        :raises NoAvailableIDs: If we could not find an available CTID.

        """

        # Error code returned by vzctl if you try to create a container with
        # a taken CTID.
        ALREADY_EXISTS = 44

        # We'll try to create the container multiple times. This may be
        # necessary because if another process is creating containers (or
        # perhaps the sysadmin is) by the time we select an available CTID
        # it could be taken already.
        retries_left = 3 # We'll decrement this counter with each retry
        while True:
            # Figure out what IDs are available
            available_ids = \
                set(self.id_range) - set(self._get_containers(False))

            if not available_ids:
                log.error("Could not find an available ID in %r.",
                    (self.id_range, ))
                raise RuntimeError("No available IDs in range.")

            # Get a random ID (this is in the hope of preventing the vmfactory
            # becoming unoperational if a particular container gets in a bad
            # state and we keep trying and failing to make a container with a
            # particular id).
            chosen_id = random.choice(list(available_ids))

            ip_address = self.allocate_ip(chosen_id)
            vzctl_args = [
                "--ipadd", ip_address,
                "--ostemplate", self.os_template,
                "--description", self.container_description
            ]

            # Actually call vzctl to create the container
            try:
                self._run_vzctl(["create", str(chosen_id)] + vzctl_args)
            except subprocess.CalledProcessError as e:
                if e.returncode == ALREADY_EXISTS:
                    retries_left -= 1
                    if retries_left > 0:
                        continue

                raise

            return {
                u"ip": ip_address,
                u"ctid": str(chosen_id)
            }

    def prepare_vm(self, vm_id, set_metadata, get_metadata):
        # Figure out the CTID of the VM from the metadata
        ctid = get_metadata(u"ctid")

        # Start the VM
        self._run_vzctl(["start", ctid])

        # Ensure that the directory we're about to install the bootstrapper
        # into actually exists.
        self._execute(ctid, "mkdir -p -m 500 %s" %
            (self.bootstrapper_directory, ))

        # Install the bootstrapper
        package_dir = os.path.dirname(galah.bootstrapper.__file__)
        for i in galah.bootstrapper.SERVER_FILES:
            self._inject_file(ctid, os.path.join(package_dir, i),
                os.path.join(self.bootstrapper_directory, i))

        # Fork off an instance of the bootstrapper
        self._execute(ctid, "%s > /dev/null 2>&1 &" % (
            os.path.join(self.bootstrapper_directory, "server.py")))

        # Create the secret we will use to auth with the bootstrapper. The
        # init dictionary will be encoded as UTF-8 so we can't just shove raw
        # binary data into the dictionary, therefore we conver to a base64
        # encoding first.
        secret = os.urandom(16).encode("base64_codec")
        set_metadata(u"bootstrapper_secret", secret)

        # Create the bootstrapper's configuration
        bootstrapper_config = {
            "user": self.guest_user,
            "group": self.guest_group,
            "harness_directory": self.harness_directory,
            "submission_directory": self.submission_directory,
            "secret": secret
        }

        # Grab the ip address of the VM, should have been set when the VM was
        # created.
        ip_address = get_metadata(u"ip")

        # Connect to the VM. We'll retry a few times to give the bootstrapper
        # time to come up.
        i = 3
        while True:
            try:
                sock = socket.create_connection(
                    (ip_address, protocol.BOOTSTRAPPER_PORT), timeout = 2)
                sock.settimeout(4)
                break
            except (socket.timeout, socket.error):
                # If we got a connection refused, it won't help to immediatley
                # try again, so we sleep for a bit here.
                time.sleep(0.5)

                i -= 1
                if i <= 0:
                    raise

        # Connect to the bootstrapper and send it its configuration
        con = protocol.Connection(sock)
        con.send(protocol.Message("init", marshal.dumps(bootstrapper_config)))
        if con.recv().command != "ok":
            raise RuntimeError("bootstrapper did not send an OK response")

    def destroy_vm(self, vm_id, get_metadata):
        ctid = get_metadata(u"ctid").encode("ascii")
        self._run_vzctl(["stop", ctid])
        self._run_vzctl(["destroy", ctid])
