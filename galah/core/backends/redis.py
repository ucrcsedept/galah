# This helps us not import ourselves
from __future__ import absolute_import

# stdlib
import time
import StringIO
import pkg_resources

# external
import redis
import mangoengine

# galah external
import galah.common.marshal

# internal
from .. import objects

# Parse the configuration file
from galah.base.config import load_config
config = load_config("core")

import logging
log = logging.getLogger("galah.core.backends.redis")

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

class RedisConnection:
    # host and port should only ever be specified during testing
    def __init__(self, host = None, port = None):
        self._redis = redis.StrictRedis(
            host = host or config["core/REDIS_HOST"],
            port = port or config["core/REDIS_PORT"]
        )

        # This will contain all of our registered scripts.
        self._scripts = {}

        # Open the LUA scripts (they are ASCII encoded because LUA isn't a
        # big fan of unicode).
        with pkg_resources.resource_stream("galah.core.backends",
                "redis-scripts.lua") as script_file:
            # Each script is delimited by a line starting with this string
            SCRIPT_DELIMITER = "----script "

            # Iterate through every line in the script file and collect each
            # script (don't register them with Redis yet).
            current_script = None # Name of the current script
            raw_scripts = {}
            for i in script_file:
                # If we found a new script
                if i.startswith(SCRIPT_DELIMITER):
                    current_script = i[len(SCRIPT_DELIMITER):].strip()
                    raw_scripts[current_script] = StringIO.StringIO()
                elif current_script is not None:
                    raw_scripts[current_script].write(i + "\n")

            # Register the scripts with Redis
            for k, v in raw_scripts.items():
                script_obj = self._redis.register_script(v.getvalue())
                self._scripts[k] = script_obj

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
            # This will get a VM off of the dirty VM queue (returning None
            # if there is no such dirty VM), set this vmfactory's
            # currently_destroying field to the VM, and then return the
            # VM's ID. This occurs atomically.
            dirty_vm_id = self._scripts["vmfactory_grab:check_dirty"](
                keys = [
                    "%s_dirty_vms" % (vmfactory_id.machine, ),
                    "vmfactory_nodes"
                ],
                args = [str(vmfactory_id)]
            )
            if dirty_vm_id == -1:
                raise RedisError(-1, "vmfactory not registered.")
            elif dirty_vm_id is not None:
                # This will be the popped VM's ID.
                return dirty_vm_id

            clean_vm_id = self._scripts["vmfactory_grab:check_clean"](
                keys = [
                    "%s_dirty_vms" % (vmfactory_id.machine, ),
                    "vmfactory_nodes"
                ],
                args = [str(vmfactory_id), 3]
            )
            if clean_vm_id == -1:
                raise RedisError(-1, "vmfactory not registered.")
            elif clean_vm_id == -2:
                raise RedisError(-2, "vmfactory already generating vm.")
            elif clean_vm_id is not None:
                return True

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
