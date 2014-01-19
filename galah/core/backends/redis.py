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
    STATE_IDLE = 0
    """The vmfactory is waiting for work."""

    STATE_CREATING_NOID = 1
    """
    The vmfactory is creating a new virtual machine and has not yet assigned
    an ID for it yet.

    """

    STATE_CREATING = 2
    """The vmfactory is creating a new virtual machine."""

    STATE_DESTROYING = 3
    """The vmfactory is destroying a dirty virtual machine."""

    state = mangoengine.IntegralField(bounds = (0, 3))
    """The state of the vmfactory."""

    vm_id = mangoengine.UnicodeField(nullable = True)
    """
    The ID of the VM the vmfactory is working with.

    When in ``STATE_CREATING``, this is the ID of the virtual machine that
    is being created and prepared.

    When in ``STATE_DESTROYING``, this is the ID of the virtual machine that
    is being destroyed.

    In all other states this attribute should be None.

    """

class _Return(Exception):
    """
    An exception raised from within functions passed to
    ``redis.StricRedis.transaction()`` that signifies that the calling
    function should return a particular value.

    """

    def __init__(self, what):
        self.what = what

class RedisConnection(object):
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

    #                             .o8
    #                            "888
    # ooo. .oo.    .ooooo.   .oooo888   .ooooo.   .oooo.o
    # `888P"Y88b  d88' `88b d88' `888  d88' `88b d88(  "8
    #  888   888  888   888 888   888  888ooo888 `"Y88b.
    #  888   888  888   888 888   888  888    .o o.  )88b
    # o888o o888o `Y8bod8P' `Y8bod88P" `Y8bod8P' 8""888P'

    def node_allocate_id(self, machine, _hints = None):
        if not isinstance(machine, unicode):
            raise TypeError("machine must be a unicode string, got %s" %
                (repr(machine), ))

        rv = self._redis.incr("LastID/%s" % (machine.encode("utf_8"), ))

        result = objects.NodeID(machine = machine, local = rv)
        result.validate()

        return result

    #  .o88o.                         .
    #  888 `"                       .o8
    # o888oo   .oooo.    .ooooo.  .o888oo  .ooooo.  oooo d8b oooo    ooo
    #  888    `P  )88b  d88' `"Y8   888   d88' `88b `888""8P  `88.  .8'
    #  888     .oP"888  888         888   888   888  888       `88..8'
    #  888    d8(  888  888   .o8   888 . 888   888  888        `888'
    # o888o   `Y888""8o `Y8bod8P'   "888" `Y8bod8P' d888b        .8'
    #                                                        .o..P'
    #                                                        `Y8P'

    def vmfactory_register(self, vmfactory_id, _hints = None):
        new_factory = VMFactory(state = VMFactory.STATE_IDLE, vm_id = None)
        new_factory.validate()
        new_factory_serialized = galah.common.marshal.dumps(
            new_factory.to_dict())

        rv = self._redis.setnx(
            "NodeInfo/%s" % (vmfactory_id.serialize(), ),
            new_factory_serialized
        )
        return rv == 1

    def vmfactory_unregister(self, vmfactory_id, _hints = None):
        vmfactory_key = "NodeInfo/%s" % (vmfactory_id.serialize(), )

        # This function performs the transaction. See Redis-Py's documentation
        # for more information on this pattern.
        def unregister(pipe):
            # Pull the vmfactory object from the database
            vmfactory_serialized = pipe.get(vmfactory_key)
            if vmfactory_serialized is None:
                raise _Return(False)
            vmfactory = VMFactory.from_dict(
                galah.common.marshal.loads(vmfactory_serialized))

            # All the Redis calls from here-on will be queued and executed
            # all at once in a transaction.
            pipe.multi()

            if vmfactory.state in (VMFactory.STATE_CREATING,
                    VMFactory.STATE_DESTROYING):
                # Destroy any VM it was working on.
                pipe.lpush(
                    "DirtyVMQueue/%s" %
                        (vmfactory_id.machine.encode("utf_8"), ),
                    vmfactory.vm_id.encode("utf_8")
                )

            # Remove the reference to the VM factory.
            pipe.delete(vmfactory_key)

        try:
            self._redis.transaction(unregister, vmfactory_key)
        except _Return as e:
            return e.what

        return True

    def vmfactory_grab(self, vmfactory_id, _hints = None):
        if _hints is None:
            _hints = {}

        # The number of seconds to wait between each poll
        poll_every = _hints.get("poll_every", 2)

        # The maximum number of clean virtual machines that can exist. Should
        # be typically pulled down from the configuration but can be
        # overridden during testing.
        max_clean_vms = _hints.get("max_clean_vms", 3)

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
                args = [vmfactory_id.serialize()]
            )
            if dirty_vm_id == -1:
                raise objects.IDNotRegistered(vmfactory_id)
            elif dirty_vm_id == -2:
                raise objects.CoreError("vmfactory is busy")
            elif dirty_vm_id != "":
                # This will be the popped VM's ID.
                return dirty_vm_id.decode("utf_8")

            clean_vm_id = self._scripts["vmfactory_grab:check_clean"](
                keys = [
                    "%s_dirty_vms" % (vmfactory_id.machine, ),
                    "vmfactory_nodes"
                ],
                args = [vmfactory_id.serialize(), max_clean_vms]
            )
            if clean_vm_id == -1:
                raise objects.IDNotRegistered(vmfactory_id)
            elif clean_vm_id == -2:
                raise objects.CoreError("vmfactory is busy")
            elif clean_vm_id == 1:
                return True

            time.sleep(poll_every)

    def vmfactory_note_clean_id(self, vmfactory_id, clean_id, _hints = None):
        if not isinstance(clean_id, unicode):
            raise TypeError("clean_id must be of type unicode, got %s" %
                (repr(clean_id), ))

        encoded_clean_id = clean_id.encode("utf_8")
        if encoded_clean_id == "":
            raise ValueError("clean_id cannot be the empty string.")

        rv = self._scripts["vmfactory_note_clean_id:note"](
            keys = ["vmfactory_nodes"],
            args = [vmfactory_id.serialize(), encoded_clean_id]
        )
        if rv == -1:
            raise objects.IDNotRegistered(vmfactory_id)
        elif rv == -2:
            raise objects.CoreError("vmfactory is not currently creating a vm")
        elif rv == -3:
            raise objects.CoreError("vmfactory already named its vm")

        return True

    def vmfactory_finish(self, vmfactory_id, _hints = None):
        with self._redis.pipeline() as pipe:
            pipe.watch("vmfactory_nodes", )

        # ----script vmfactory_finish:finish
        # -- keys = (vmfactory_nodes, clean_vms_queue), args = (vmfactory_id)
        # -- Returns 1 on success, -1 if the vmfactory wasn't registered, -2 if the
        # --     vmfactory was not assigned work, or -3 if the vmfactory has not
        # --     given an ID to a VM it was creating.

        # -- Get and decode the vmfactory object
        # local vmfactory_json = redis.call("hget", KEYS[1], ARGV[1])
        # if vmfactory_json == false then
        #     return -1
        # end
        # local vmfactory = cjson.decode(vmfactory_json)

        # if vmfactory["currently_creating"] ~= cjson.null then
        #     if vmfactory["currently_creating"] == "" then
        #         return -3
        #     end

        #     redis.call("lpush", KEYS[2], vmfactory["currently_creating"])
        #     vmfactory["currently_creating"] = cjson.null
        # else if vmfactory["currently_destroying"] ~= cjson.null then
        #     vmfactory["currently_destroying"] = cjson.null
        # else
        #     return -2
        # end

        # redis.call("hset", KEYS[1], ARGV[1], cjson.encode(vmfactory))

        # return 1

    # oooooo     oooo ooo        ooooo
    #  `888.     .8'  `88.       .888'
    #   `888.   .8'    888b     d'888   .oooo.o
    #    `888. .8'     8 Y88. .P  888  d88(  "8
    #     `888.8'      8  `888'   888  `"Y88b.
    #      `888'       8    Y     888  o.  )88b
    #       `8'       o8o        o888o 8""888P'

    def vm_mark_dirty(self, vmfactory_id, vm_id, _hints = None):
        if not isinstance(vm_id, unicode):
            raise TypeError("vm_id must be a unicode string, got %s." %
                (repr(vm_id), ))

        vm_id_encoded = vm_id.encode("utf_8")
        if vm_id_encoded == "":
            raise ValueError("vm_id cannot be the empty string")

        self._redis.lpush("%s_dirty_vms" % (vmfactory_id.machine, ),
            vm_id_encoded)

        return True
