# external
import redis
import mangoengine
import time

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
    currently_creating = mangoengine.ModelField(objects.NodeID)

_LUA_SCRIPTS = {
"vmfactory_grab:check_dirty":
"""
local dirty_vm_id = redis.call("rpop", KEYS[1])
if dirty_vm_id == false then
    return false
end

-- Get and decode the vmfactory object
local rv = redis.call("hget", KEYS[2], ARGV[1])
if rv == false then
    return -1
end
local vmfactory = cjson.decode(rv)

-- Set the currently_destroying key and persist the change
vmfactory["currently_destroying"] = dirty_vm_id
redis.call("hset", KEYS[2], ARGV[1], cjson.encode(vmfactory))

return dirty_vm_id
"""
}

class RedisConnection:
    # host and port should only ever be specified during testing
    def __init__(self, host = None, port = None):
        self._redis = redis.StrictRedis(
            host = host or config["core/REDIS_HOST"],
            port = port or config["core/REDIS_PORT"]
        )

        # This will register the LUA scripts with Redis and make them
        # accessible to us via the _scripts dictionary.
        self._scripts = {}
        for k, v in _LUA_SCRIPTS.items():
            self._scripts[k] = self._redis.register_script(v)

    def vmfactory_register(self, vmfactory_id, _hints = None):
        INITIAL_DATA = _VMFactoryNode(
            currently_destroying = u"",
            currently_creating = u""
        )

        rv = self._redis.hsetnx("vmfactory_nodes", str(vmfactory_id),
            galah.common.marshal.dumps(INITIAL_DATA.to_dict()))

        # Returns True if we're already registered, False otherwise
        return rv != 1

    def vmfactory_unregister(self, vmfactory_id, _hints = None):
        rv = self._redis.hdel("vmfactory_nodes", str(vmfactory_id))
        if rv != 1:
            raise RedisError(rv, "vmfactory not registered.")

    def vmfactory_lookup(self, vmfactory_id, _hints = None):
        rv = self._redis.hget("vmfactory_nodes", str(vmfactory_id))
        if rv is None:
            raise RedisError(rv, "vmfactory not registered.")

        # Deserialize the data
        rv_dict = galah.common.marshal.loads(rv)

        return _VMFactoryNode.from_dict(rv_dict)

    def vmfactory_grab(self, vmfactory_id, _hints = None):
        if _hints is None:
            _hints = {}

        poll_every = _hints.get("poll_every", 2)
        while True:
            rv = self._scripts["vmfactory_grab:check_dirty"](
                keys = ["%s_dirty_vms" % (vmfactory_id.machine, ), "vmfactory_nodes"],
                args = [str(vmfactory_id)]
            )
            if rv is not None:
                return rv

            time.sleep(poll_every)

        # poll every few seconds (set by hint with sensible default) to see if
        # the number of clean vms is too low or there's any dirty vms

        # pop a vm off (machine_id)_dirty_vms
        # set vmfactory_nodes[vmfactory_id].currently_destroying to vmfactory_id of popped vm
        # return vm vmfactory_id

        # increment (machine_id)_num_clean_vms
        # create new vm in (machine_id)_vms marked as clean but being created
        # set vmfactory_nodes[vmfactory_id].currently_creating to the new VM vmfactory_id
        # return vm vmfactory_id
