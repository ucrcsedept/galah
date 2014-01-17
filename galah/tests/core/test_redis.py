# internal
from galah.core.backends.redis import *
from galah.core.objects import *

# test internal
from .pytest_redis import parse_redis_config

# external
import pytest

# Tell pytest to load our pytest_redis plugin. Absolute import is required here
# though I'm not sure why. It does not error when given simply "pytest_redis"
# but it does not correclty load the plugin.
pytest_plugins = ("galah.tests.core.pytest_redis", )

class TestVMFactory:
    def test_registration(self, redis_server):
        con = RedisConnection(redis_server)

        my_id = NodeID(machine = u"localhost", local = u"pytest")

        # Try to unregister out not registered node
        assert not con.vmfactory_unregister(my_id)

        # Register our node
        assert con.vmfactory_register(my_id)

        # Re-register our node
        assert not con.vmfactory_register(my_id)

        # Unregister our node
        assert con.vmfactory_unregister(my_id)

        # Unregister our node again
        assert not con.vmfactory_unregister(my_id)
