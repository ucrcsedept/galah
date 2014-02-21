# internal
import galah.vmfactory.providers.vz as vzprovider
from galah.core.objects import NodeID
import galah.bootstrapper.protocol as protocol

# external
import pytest

# stdlib
import sys
import socket
import os

@pytest.fixture
def vz(request):
    try:
        provider = vzprovider.OpenVZProvider()
    except:
        pytest.skip("Could not create OpenVZ provider.")

    if not os.path.exists(provider.vzctl_path):
        pytest.skip("Configured path of vzctl (%r) does not exist.",
            provider.vzctl_path)

    # This will prevent containers created during testing from being picked up
    # incidently by a running vmfactory in the event of an ID range overlap.
    provider.container_description = "galah-created:test"

    # The output of vzctl and any other commands are sent to the NULL_FILE
    # which is normally /dev/null. We want to actually see the output of these
    # commands instead, so we'll point NULL_FILE at stderr
    vzprovider.NULL_FILE = sys.stderr

    return provider

class TestOpenVZProvider:
    """
    Tests to ensure that the OpenVZProvider class works as expected.

    .. warning::

        Make sure that the IDs being used in testing are not being used by
        anything else (including you) while the tests are running otherwise the
        tests may give false results.

        This can be done by changing the configuration option
        ``vmfactory/vz/ID_RANGE1`` when running the tests to a different range
        than any running vmfactory.

    """

    def test_run_vzctl_smoke(self, vz):
        """A smoke test to make sure that ``vzctl`` is available."""

        assert vz._run_vzctl(["--version"]) == 0

    def test_get_containers_smoke(self, vz):
        """A smoke test to make sure that ``_get_containers`` doesn't error."""

        vz._get_containers(False)
        vz._get_containers(True)

    def test_create_destroy(self, vz):
        """Tests creating and destroying a virtual machine."""

        # Save all the containers that exist on the system
        containers_before = vz._get_containers(False)
        print "Containers extant before creation: %r" % (containers_before, )

        try:
            # Create a new container
            created_vm_metadata = vz.create_vm()
            assert isinstance(created_vm_metadata, dict)
            print "Created VM Metadata: ", repr(created_vm_metadata)
        finally:
            # Save all the containers taht exist afterr the creation
            containers_after = vz._get_containers(False)
            print "Containers extant after creation: %r" % (containers_after, )

            # This will tell you if there was any created containers (though
            # it could get fooled by other VMs getting created at the same
            # time or various other race conditions)
            print "Difference: %r" % (
                set(containers_after) - set(containers_before), )

        # Pull out the CTID from the metadata
        ctid = int(created_vm_metadata["ctid"])

        # Make sure that we can see the CTID in the listing of all containers
        assert ctid in vz._get_containers(True)
        assert ctid in vz._get_containers(False)

        # The destroy_vm function needs a way to query the metadata, so we'll
        # make a dummy function here. Normally this would be a function that
        # makes a call to redis-py.
        def get_metadata(key):
            return created_vm_metadata[key]

        # Likewise, the destroy_vm function also needs a NodeID, we'll create a
        # fake one here.
        vm_nodeid = NodeID(machine = u"localhost", local = 1)

        assert vz.destroy_vm(vm_nodeid, get_metadata) is None
        assert ctid not in vz._get_containers(True)
        assert ctid not in vz._get_containers(False)

    def test_prepare(self, vz):
        # Create a new container
        created_vm_metadata = vz.create_vm()

        # Pull out the CTID from the metadata
        ctid = int(created_vm_metadata["ctid"])

        # Get some dummy objects prepared that prepare_vm and destroy_vm can
        # play with.
        get_metadata = created_vm_metadata.__getitem__
        set_metadata = created_vm_metadata.__setitem__
        vm_nodeid = NodeID(machine = u"localhost", local = 1)

        try:
            # After this completes the bootstrapper should be running on the
            # VM.
            vz.prepare_vm(ctid, set_metadata, get_metadata)

            # Connect to the bootstrapper
            sock = socket.create_connection((created_vm_metadata["ip"],
                protocol.BOOTSTRAPPER_PORT), timeout = 2)
            con = protocol.Connection(sock)

            # Authenticate with the bootstrapper
            con.send(protocol.Message("auth",
                created_vm_metadata["bootstrapper_secret"]))
            assert con.recv().command == "ok"

            # Grab the configuration it received
            con.send(protocol.Message("get_config", ""))
            response = con.recv()
            assert response.command == "config"
            print response.payload
        finally:
            # At least try and destroy the VM if anything bad happens
            vz.destroy_vm(vm_nodeid, get_metadata)
