# internal
from galah.core.backends.redis import *
from galah.core.objects import *

# test internal
from .pytest_redis import parse_redis_config

# external
import pytest

# A crazy unicode string suitable for use in testing. Prints as
# "THE PONY HE COMES" with tons of decoration.
UNICODE_TEST_PONY = (
    u"TH\u0318E\u0344\u0309\u0356 \u0360P\u032f\u034d\u032dO\u031a\u200bN"
    u"\u0310Y\u0321 H\u0368\u034a\u033d\u0305\u033e\u030e\u0321\u0338\u032a"
    u"\u032fE\u033e\u035b\u036a\u0344\u0300\u0301\u0327\u0358\u032c\u0329 "
    u"\u0367\u033e\u036c\u0327\u0336\u0328\u0331\u0339\u032d\u032fC\u036d\u030f"
    u"\u0365\u036e\u035f\u0337\u0319\u0332\u031d\u0356O\u036e\u034f\u032e\u032a"
    u"\u031d\u034dM\u034a\u0312\u031a\u036a\u0369\u036c\u031a\u035c\u0332\u0316"
    u"E\u0311\u0369\u034c\u035d\u0334\u031f\u031f\u0359\u031eS\u036f\u033f"
    u"\u0314\u0328\u0340\u0325\u0345\u032b\u034e\u032d"
)

# Another crazy unicode string that renders as mostly scribbles.
UNICODE_TEST_SCRIBBLES = (
    u" \u031b \u0340 \u0341 \u0358 \u0321 \u0322 \u0327 \u0328 \u0334 \u0335 "
    u"\u0336 \u034f \u035c \u035d \u035e \u035f \u0360 \u0362 \u0338 \u0337 "
    u"\u0361 \u0489"
)

# Tell pytest to load our pytest_redis plugin. Absolute import is required here
# though I'm not sure why. It does not error when given simply "pytest_redis"
# but it does not correclty load the plugin.
pytest_plugins = ("galah.tests.core.pytest_redis", )

class TestNode:
    def test_allocate(self, redis_server):
        con = RedisConnection(redis_server)

        id1 = con.node_allocate_id(UNICODE_TEST_PONY)
        id2 = con.node_allocate_id(UNICODE_TEST_PONY)
        id3 = con.node_allocate_id(UNICODE_TEST_PONY)
        assert id1 != id2 and id1 != id3 and id2 != id3

        with pytest.raises(TypeError):
            # The argument must be a unicode string
            con.node_allocate_id("localhost")

        with pytest.raises(TypeError):
            # The argument must be a unicode string
            con.node_allocate_id(2)

class TestVMFactory:
    def test_registration(self, redis_server):
        """
        Basic test to ensure that registering and unregistering VMs work to
        some degree.

        """

        con = RedisConnection(redis_server)

        my_id = NodeID(machine = UNICODE_TEST_PONY, local = 0)

        # Try to unregister our not registered node
        assert not con.vmfactory_unregister(my_id)

        # Register our node
        assert con.vmfactory_register(my_id)

        # Re-register our node
        assert not con.vmfactory_register(my_id)

        # Unregister our node
        assert con.vmfactory_unregister(my_id)

        # Unregister our node again
        assert not con.vmfactory_unregister(my_id)

    def test_grab_clean(self, redis_server):
        """
        Tests grab to ensure that it will return True when there are no queued
        VMs waiting for deletion.

        """

        con = RedisConnection(redis_server)

        my_id = NodeID(machine = UNICODE_TEST_PONY, local = 0)
        assert con.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 2}

        # This should tell us to make a clean virtual machine
        assert con.vmfactory_grab(my_id, grab_hints)

        # The last grab should have assigned us the work, so this should error
        # out.
        with pytest.raises(CoreError):
            con.vmfactory_grab(my_id, grab_hints)

    def test_grab_dirty(self, redis_server):
        """
        This test ensures that we get a dirty VM from grab if there is one
        queued.

        """

        con = RedisConnection(redis_server)

        my_id = NodeID(machine = UNICODE_TEST_PONY, local = 0)
        assert con.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 2}

        fake_vm_id = UNICODE_TEST_SCRIBBLES
        assert con.vm_mark_dirty(my_id, fake_vm_id)

        fake_vm_id2 = UNICODE_TEST_PONY
        assert con.vm_mark_dirty(my_id, fake_vm_id)

        dirty_vm = con.vmfactory_grab(my_id, grab_hints)
        assert dirty_vm == fake_vm_id
        assert isinstance(dirty_vm, unicode)

        # We are already assigned work so this should fail
        with pytest.raises(CoreError):
            con.vmfactory_grab(my_id, grab_hints)

    def test_workflow_clean(self, redis_server):
        """
        This tests performs all of the calls a vmfactory who is creating
        clean VMs would make while performing its duties.

        """

        con = RedisConnection(redis_server)

        my_id = NodeID(machine = UNICODE_TEST_PONY, local = 0)
        assert con.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 20}

        # We should be able to continually perform these operations so we'll
        # do them ten times here.
        for i in range(10):
            # This should tell us to make a clean virtual machine
            assert con.vmfactory_grab(my_id, grab_hints)

            with pytest.raises(CoreError):
                con.vmfactory_finish(my_id)

            # We'll pretend we created a machine and named it something
            fake_vm_id = UNICODE_TEST_SCRIBBLES
            assert con.vmfactory_note_clean_id(my_id, fake_vm_id)

            assert con.vmfactory_finish(my_id)

            with pytest.raises(CoreError):
                con.vmfactory_finish(my_id)

    # def test_workflow_dirty(self, redis_server):
    #     con = RedisConnection(redis_server)

    #     my_id = NodeID(machine = u"localhost", local = 0)
    #     assert con.vmfactory_register(my_id)

    #     grab_hints = {"max_clean_vms": 20}

    #     fake_vm_id = u"101"
    #     assert con.vm_mark_dirty(my_id, fake_vm_id)

    #     # We should be able to continually perform these operations so we'll
    #     # do them ten times here.
    #     for i in range(10):
    #         # This should tell us to make a clean virtual machine
    #         assert con.vmfactory_grab(my_id, grab_hints)

    #         with pytest.raises(CoreError):
    #             con.vmfactory_finish(my_id)

    #         # We'll pretend we created a machine and named it something
    #         fake_vm_id = u"101"
    #         assert con.vmfactory_note_clean_id(my_id, fake_vm_id)

    #         assert con.vmfactory_finish(my_id)

    #         with pytest.raises(CoreError):
    #             con.vmfactory_finish(my_id)
