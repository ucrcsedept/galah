# external
import redis
import mangoengine

# galah external
import galah.common.json

# internal
from . import objects

# Parse the configuration file
from galah.base.config import load_config
config = load_config("core")

log = logging.getLogger("galah.core.redis")

class _VMFactoryNode(mangoengine.Model):
    currently_destroying = mangoengine.ModelField(objects.NodeID)
    currently_cleaning = mangoengine.ModelField()

class RedisConnection:
    # host and port should only ever be specified during testing
    def __init__(self, host = None, port = None):
        self._redis = redis.StrictRedis(
            host = host or config["core/REDIS_HOST"],
            port = port or config["core/REDIS_PORT"]
        )

    def vmfactory_register(self, id):
        INITIAL_DATA = {
            "currently_cleaning": "",
            "currently_destroying": ""
        }

        self._redis.hsetnx("vmfactory_nodes", str(id),
            galah.common.json.dumps()
