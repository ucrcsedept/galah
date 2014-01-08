# external
import redis
import mangoengine

# galah external
import galah.common.marshal

# internal
from . import objects

# Parse the configuration file
from galah.base.config import load_config
config = load_config("core")

import logging
log = logging.getLogger("galah.core.redis")

class RedisError(RuntimeError):
    def __init__(self, return_value, description):
        self.return_value = return_value
        self.description = description

        super(RedisError, self).__init__(self)

    def __str__(self):
        "%s (Redis returned %d)" % (self.description, self.return_value)

class _VMFactoryNode(mangoengine.Model):
    currently_destroying = mangoengine.ModelField(objects.NodeID)
    currently_cleaning = mangoengine.ModelField(objects.NodeID)

class RedisConnection:
    # host and port should only ever be specified during testing
    def __init__(self, host = None, port = None):
        self._redis = redis.StrictRedis(
            host = host or config["core/REDIS_HOST"],
            port = port or config["core/REDIS_PORT"]
        )

    def vmfactory_register(self, id):
        INITIAL_DATA = _VMFactoryNode(
            currently_destroying = "",
            currently_cleaning = ""
        )

        rv = self._redis.hsetnx("vmfactory_nodes", str(id),
            galah.common.marshal.dumps(INITIAL_DATA.to_dict()))
        if rv != 1:
            raise RedisError(rv, "vmfactory already registered.")

    def vmfactory_unregister(self, id):
        rv = self._redis.hdel("vmfactory_nodes", str(id))
        if rv != 1:
            raise RedisError(rv, "vmfactory not registered.")
