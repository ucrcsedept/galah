# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

import galah.sheep.utility.exithelpers as exithelpers
from galah.sheep.utility.testrequest import PreparedTestRequest
import pyvz
import time
import Queue
import socket
import os
import os.path
import json
import datetime

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep/vz")

containers = Queue.Queue(maxsize = config["MAX_MACHINES"])

# Performs one time setup for the entire module
def setup(logger):
    if config["MAX_MACHINES"] == 0:
        logger.warning(
            "MAX_MACHINES is 0. Infinitely many virtual machines will be "
            "created. If this is not what you want (which it probably isn't), "
            "stop this sheep and edit the configuration file."
        )

    # Get a list of all of the clean virtual machines that already exist
    clean_machines = pyvz.get_containers("galah-vm: clean")

    # Add all the clean VMs to the queue
    while clean_machines:
        m = clean_machines.pop()

        try:
            containers.put_nowait(m)
        except Queue.Full:
            break

        logger.info("Reusing clean VM with CTID %d." % m)

    # Any remaining virtual machines will simply be shut down. This is a bit of
    # a waste but makes it easier to handle. No reason not to come back and add
    # logic to use these in the future.
    for i in clean_machines:
        logger.info("Destroying clean VM with CTID %d.", i)

        try:
            pyvz.extirpate_container(i)
        except SystemError:
            logger.exception(
                "Could not destroy clean VM with CTID %d during setup.", i
            )

    # Get a list of all the dirty virtual machines
    dirty_machines = pyvz.get_containers("galah-vm: dirty")
    for i in dirty_machines:
        self.logger.info("Destroying dirty VM with CTID %d.", i)

        try:
            pyvz.extirpate_container(i)
        except SystemError:
            self.logger.exception("Could not destroy dirty VM with CTID %d.", i)

class Producer:
    def __init__(self, logger):
        self.logger = logger
        self._last_low_machine_log = datetime.datetime.min

    def produce_vm(self):
        if containers.full():
            self.logger.info("MAX_MACHINES machines exist. Waiting...")

            exithelpers.wait_for_queue(containers)

        # Check to see if we are low on virtual machines.
        if (self._last_low_machine_log + config["LOW_MACHINE_PERIOD"] <
                datetime.datetime.today() and
                containers.qsize() < config["LOW_MACHINE_THRESHOLD"]):
            self.logger.warning(
                "VM cache is below LOW_MACHINE_THRESHOLD (%d). The current "
                "number of VMs in the cache is %d.",
                config["LOW_MACHINE_THRESHOLD"],
                containers.qsize()
            )

        self.logger.debug("Creating new VM.")

        try:
            # Create new container with unique id
            id = pyvz.create_container(
                os_template = config["OS_TEMPLATE"],
                description = "galah-vm: clean",
                subnet = config["VM_SUBNET"]
            )
        except (RuntimeError, SystemError):
            self.logger.exception("Error occured when creating VM")

            # Sleep for a bit and then try again
            time.sleep(5)
            return None

        self.logger.debug("Created new VM with CTID %d" % id)

        try:
            # Start container
            pyvz.start_container(id)
        except SystemError:
            self.logger.exception("Could not start VM with CTID %d" % id)

            try:
                pyvz.extirpate_container(id)
            except SystemError:
                # This is when the sys admin should start panicking. Seriously
                # bad mojo-jo-jo right here.
                self.logger.critical(
                    "Could not destroy non-starting VM with CTID %d!!! VM will "
                    "not be destroyed. Manual destruction is required. If this "
                    "occurs repeatedly, this sheep must be killed, otherwise "
                    "dead VMs will fill the system!" % id
                )

                # Wait for a minute before trying again.
                time.sleep(60)

            return None

        # Try to add the container to the queue until successful or the program
        # is exiting.
        exithelpers.enqueue(containers, id)

        self.logger.info("Added VM with CTID %d to the queue" % id)

        return id

class Consumer:
    def __init__(self, logger):
        self.logger = logger

    def prepare_machine(self):
        return exithelpers.dequeue(containers)

    def run_test(self, container_id, test_request):
        self.logger.debug("Running test with VM with CTID %d.", container_id)

        try:
            # Mark container as dirty before we do anything at all
            pyvz.set_attribute(container_id, "description", "galah-vm: dirty")
        except SystemError:
            self.logger.exception(
                "Error occured during setup, destroying VM with CTID %d.", container_id
            )

            try:
                pyvz.extirpate_container(container_id)
            except SystemError:
                self.logger.exception("Could not destroy VM with CTID %d.", container_id)

            return None

        try:
            # Figure out where the user's testables are stored
            testable_directory = os.path.join(
                config["SUBMISSION_DIRECTORY"],
                test_request["submission"]["assignment"],
                test_request["submission"]["user"],
                test_request["submission"]["id"]
            )

            # Figure out where the test harness is
            harness_directory = os.path.join(
                config["HARNESS_DIRECTORY"], test_request["test_harness"]["id"]
            )

            self.logger.debug(
                "Injecting testables at '%s' and harness at '%s'." %
                    (testable_directory, harness_directory)
            )

            if config["CALL_MKDIR"]:
                pyvz.execute(
                    container_id,
                    "mkdir -p %s %s" % (
                        config["VM_TESTABLES_DIRECTORY"],
                        config["VM_HARNESS_DIRECTORY"]
                    )
                )

            # Inject file into VM from the testables location
            pyvz.inject_file(
                container_id, testable_directory, config["VM_TESTABLES_DIRECTORY"]
            )

            # Ditto from the test harness's location
            pyvz.inject_file(container_id, harness_directory, config["VM_HARNESS_DIRECTORY"])

            # Inject bootstrapper (which is responsible for running inside of
            # the virtual machine with root privelages and starting up the test
            # harness while communicating with us).
            self.logger.debug(
                "Running bootstrapper at '%s'." % config["BOOTSTRAPPER"]
            )
            pyvz.inject_file(container_id, config["BOOTSTRAPPER"], "/tmp/")
            pyvz.run_script(
                container_id,
                os.path.join("/tmp/", os.path.basename(config["BOOTSTRAPPER"]))
            )

            # Bind to a good ole' fashioned tcp socket and wait for the
            # bootstrapper to connect to us.
            bootstrapper = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bootstrapper.setblocking(1)
            bootstrapper.settimeout(60)

            # Try to connect to the bootstrapper
            deadline = time.time() + 30
            while time.time() <= deadline:
                try:
                    bootstrapper.connect(
                        ("%s.%d" % (config["VM_SUBNET"], container_id), config["VM_PORT"])
                    )

                    self.logger.debug(
                        "Connected to %s.%d:%d.",
                        config["VM_SUBNET"], container_id, config["VM_PORT"]
                    )

                    break
                except socket.error:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Could not connect to bootstrapper.")

            # TODO: Bring this out of the virtual suite. Plz.
            prepared_request = PreparedTestRequest(
                raw_harness = test_request["test_harness"],
                raw_submission = test_request["submission"],
                raw_assignment = test_request["assignment"],
                testables_directory = config["VM_TESTABLES_DIRECTORY"],
                harness_directory = config["VM_HARNESS_DIRECTORY"],
                suite_specific = {
                    "vz/uid": config["TESTUSER_UID"],
                    "vz/gid": config["TESTUSER_GID"]
                }
            )
            prepared_request.update_actions()
            prepared_request = prepared_request.to_dict()

            self.logger.debug(
                "Test request being sent to bootstrapper: %s",
                str(prepared_request)
            )

            # Chuck the test request at the bootstrapper
            bootstrapper.send(json.dumps(prepared_request))
            bootstrapper.shutdown(socket.SHUT_WR)

            try:
                # Receive test results from the VM
                self.logger.debug("Waiting for test results from bootstrapper.")
                results = []
                while True:
                    received = bootstrapper.recv(4096)

                    if not received:
                        break

                    results.append(received)
                results = "".join(results)

                self.logger.debug("Test results recieved %s.", results)
            except socket.timeout:
                self.logger.debug("Bootstrapper timed out")

                return None

            try:
                return json.loads(results)
            except ValueError:
                return None
        finally:
            self.logger.debug("Destroying VM with CTID %d" % container_id)

            try:
                pyvz.extirpate_container(container_id)
            except SystemError:
                self.logger.critical(
                    "Could not destroy container with container_id %s.", str(container_id)
                )
