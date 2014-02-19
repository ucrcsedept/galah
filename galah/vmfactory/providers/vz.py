# stdlib
import subprocess
import os
import random
from datetime import datetime, timedelta

# internal
from .base import BaseProvider

import logging
log = logging.getLogger("galah.vmfactory")

from galah.base.config import load_config
config = load_config("")

NULL_FILE = open(os.devnull, "w")

class OpenVZProvider(BaseProvider):
    container_description = "galah-created"

    def __init__(self, vzctl_path = None, vzlist_path = None, id_range = None,
            allocate_ip = None, os_template = None, container_directory = None,
            guest_user = None):
        self.vzctl_path = (vzctl_path if vzctl_path is not None else
            config["vmfactory/vz/VZCTL_PATH"])
        self.vzlist_path = (vzlist_path if vzlist_path is not None else
            config["vmfactory/vz/VZLIST_PATH"])
        self.id_range = (id_range if id_range is not None else
            config["vmfactory/vz/ID_RANGE"])
        self.allocate_ip = (allocate_ip if allocate_ip is not None else
            config["vmfactory/vz/ALLOCATE_IP"])
        self.os_template = (os_template if os_template is not None else
            config["vmfactory/vz/OS_TEMPLATE"])
        self.container_directory = (
            container_directory if container_directory is not None else
            config["vmfactory/vz/CONTAINER_DIRECTORY"])
        self.guest_user = (guest_user if guest_user is not None else
            config["vmfactory/GUEST_USER"])

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

    def _inject_file(self, container, source_path, dest_path):
        """
        Injects a file from the host system into the filesystem of the
        given container.

        :param container: The container ID to inject the file into.
        :param source_path: The path to the file on the host system.
        :param dest_path: The path on the guest to copy the file to.

        """

        # Figure out the path on the host system of the dest_path (remember
        # that the guest filesystem is visible to us)
        if dest_path[0] != "/":
            raise ValueError("dest_path must be an absolute path")
        real_dest_path = os.path.join(self.container_directory, container,
            dest_path[1:])

        # Do the actual copy
        subprocess.check_call(["cp", "-rf", source_path, real_dest_path],
            stdout = NULL_FILE, stderr = NULL_FILE)

        # Ensure that the permissions are set correctly (read and execute only
        # by owner) and owned by the corret guest_user.
        subprocess.check_call(["chown", "-R", self.guest_user, real_dest_path],
            stdout = NULL_FILE, stderr = NULL_FILE)
        subprocess.check_call(["chmod", "-R", "500", real_dest_path],
            stdout = NULL_FILE, stderr = NULL_FILE)

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

    def destroy_vm(self, vm_id, get_metadata):
        self._run_vzctl(["destroy", get_metadata(u"ctid").encode("ascii")])
