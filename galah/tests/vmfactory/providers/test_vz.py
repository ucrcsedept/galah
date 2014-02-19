# internal
import galah.vmfactory.providers.vz as vzprovider
from galah.core.objects import NodeID

# external
import pytest

# stdlib
import sys

@pytest.fixture
def vz(request):
    raw_config = request.config.getoption("--openvz")
    if not raw_config:
        pytest.skip("Configuration with `--openvz` required for this test.")
    config = eval(raw_config)

    provider = vzprovider.OpenVZProvider(**config)

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

