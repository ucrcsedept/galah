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

class RedisError(objects.BackendError):
    def __init__(self, return_value, description):
        self.return_value = return_value
        self.description = description

        super(RedisError, self).__init__(self)

    def __str__(self):
        return "%s (Redis returned %d)" % (self.description, self.return_value)

class VMFactory(mangoengine.Model):
    currently_destroying = mangoengine.UnicodeField(nullable = True)
    currently_creating = mangoengine.UnicodeField(nullable = True)

class RedisConnection:
    # redis_connection should only ever be specified during testing
    def __init__(self, redis_connection = None):
        if redis_connection is None:
            self._redis = redis.StrictRedis(
                host = config["core/REDIS_HOST"],
                port = config["core/REDIS_PORT"]
            )
        else:
            self._redis = redis_connection

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
        INITIAL_DATA = VMFactory(
            currently_destroying = u"",
            currently_creating = u""
        )

        rv = self._redis.hsetnx("vmfactory_nodes", vmfactory_id.serialize(),
            galah.common.marshal.dumps(INITIAL_DATA.to_dict()))

        # hsetnx will only make the change if the field did not exist to
        # begin with. If it did exist, it will return 0, otherwise it will
        # return 1.
        return rv == 1

    def vmfactory_unregister(self, vmfactory_id, _hints = None):
        rv = self._scripts["vmfactory_unregister:unregister"](
            keys = [
                "vmfactory_nodes",
                "%s_dirty_vms" % (vmfactory_id.machine, )
            ],
            args = [vmfactory_id.serialize()]
        )

        # Our script will return 1 if the vmfactory was registered and 0
        # otherwise. Error conditions will be transformed into exceptions by
        # pyredis automatically.
        return rv == 1

    def vmfactory_grab(self, vmfactory_id, _hints = None):
        if _hints is None:
            _hints = {}

        # The number of seconds to wait between each poll
        poll_every = _hints.get("poll_every", 2)

        while True:
            # This will get a VM off of the dirty VM queue (returning ""
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
                raise objects.IDNotRegistered(vmfactory_id)
            elif dirty_vm_id == -2:
                raise objects.CoreError("vmfactory is busy")
            elif dirty_vm_id != "":
                # This will be the popped VM's ID.
                return objects.VirtualMachineID.deserialize(dirty_vm_id)

            clean_vm_id = self._scripts["vmfactory_grab:check_clean"](
                keys = [
                    "%s_dirty_vms" % (vmfactory_id.machine, ),
                    "vmfactory_nodes"
                ],
                args = [str(vmfactory_id), 3]
            )
            if clean_vm_id == -1:
                raise objects.IDNotRegistered(vmfactory_id)
            elif clean_vm_id == -2:
                raise objects.CoreError("vmfactory is busy")
            elif clean_vm_id == 1:
                return True

            time.sleep(poll_every)
