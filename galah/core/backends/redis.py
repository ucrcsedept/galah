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
config = load_config("")

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
    The vmfactory is creating a new virtual machine and has not yet registered
    an ID for it yet.

    """

    STATE_CREATING = 2
    """The vmfactory is creating a new virtual machine."""

    STATE_DESTROYING = 3
    """The vmfactory is destroying a dirty virtual machine."""

    state = mangoengine.IntegralField(bounds = (0, 3))
    """The state of the vmfactory."""

    vm_id = mangoengine.StringField(nullable = True)
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

    This is not an exception in the traditional sense, rather it is a tool
    used to send messages out of the transaction functions.

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

        clean_vm_count_key = "CleanVMCount/%s" % (
            vmfactory_id.machine.encode("utf_8"), )

        # This function performs the transaction. See Redis-Py's documentation
        # for more information on this pattern.
        def unregister(pipe):
            # watch(vmfactory_key, clean_vm_count_key)

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

            # If we were in the middle of creating a VM we want to decrement
            # the current count of VMs.
            if vmfactory.state in (VMFactory.STATE_CREATING,
                    VMFactory.STATE_CREATING_NOID):
                pipe.decr(clean_vm_count_key)

            # Remove the reference to the VM factory.
            pipe.delete(vmfactory_key)

        try:
            self._redis.transaction(unregister, vmfactory_key,
                clean_vm_count_key)
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
        max_clean_vms = _hints.get("max_clean_vms", 2)

        vmfactory_key = "NodeInfo/%s" % (vmfactory_id.serialize(), )

        # Will check to see if there is a dirty virtual machine waiting to be
        # deleted. If there is no such VM, _Return(None) is raised. If there
        # is one, it can be retrieved by examining the first result in the
        # transaction.
        dirty_queue_key = "DirtyVMs/%s" % (
            vmfactory_id.machine.encode("utf_8"), )
        def check_dirty(pipe):
            # watch(dirty_queue_key, vmfactory_key)

            vmfactory_json = pipe.get(vmfactory_key)
            if vmfactory_json is None:
                raise objects.IDNotRegistered(vmfactory_id)
            vmfactory = VMFactory.from_dict(
                galah.common.marshal.loads(vmfactory_json))
            if vmfactory.state != VMFactory.STATE_IDLE:
                raise objects.CoreError("vmfactory is busy")

            # This will peek at the last element in the list
            dirty_vm_id_local = pipe.lindex(dirty_queue_key, -1)
            if dirty_vm_id_local is None:
                raise _Return(None)

            # Only the local part of the VM's ID is stored within the queue, so
            # create the full ID now.
            dirty_vm_id = objects.NodeID(machine = vmfactory_id.machine,
                local = int(dirty_vm_id_local))

            # All following Redis calls will be buffered and executed at once
            # as a transaction.
            pipe.multi()

            # Actually pop the last item from the dirty vm queue
            pipe.rpop(dirty_queue_key)

            # Change the VM factory's state
            vmfactory.state = VMFactory.STATE_DESTROYING
            vmfactory.vm_id = dirty_vm_id.serialize()
            pipe.set(vmfactory_key,
                galah.common.marshal.dumps(vmfactory.to_dict()))

        # If this transaction does not raise _Return(None) then the vmfactory
        # should begin producing a new clean virtual machine.
        clean_vm_count_key = "CleanVMCount/%s" % (
            vmfactory_id.machine.encode("utf_8"), )
        def check_clean(pipe):
            # watch(clean_vm_count_key, vmfactory_key)

            num_clean_vms = pipe.get(clean_vm_count_key)
            if (num_clean_vms is not None and
                    int(num_clean_vms) >= max_clean_vms):
                raise _Return(None)

            vmfactory_json = pipe.get(vmfactory_key)
            if vmfactory_json is None:
                raise objects.IDNotRegistered(vmfactory_id)
            vmfactory = VMFactory.from_dict(
                galah.common.marshal.loads(vmfactory_json))
            if vmfactory.state != VMFactory.STATE_IDLE:
                raise CoreError("vmfactory is busy")

            # All following calls to redis will be queued as part of the
            # transaction.
            pipe.multi()

            vmfactory.state = VMFactory.STATE_CREATING_NOID
            pipe.set(vmfactory_key,
                galah.common.marshal.dumps(vmfactory.to_dict()))

            # We increment this before we actually create the VM so other
            # vmfactories don't end up making more virtual machines than
            # necessary.
            pipe.incr(clean_vm_count_key)

        while True:
            try:
                result = self._redis.transaction(check_dirty,
                    dirty_queue_key, vmfactory_key)
            except _Return as e:
                # The check_dirty function raises _Return(None) if we should
                # *not* start destroying a virtual machine.
                assert e.what is None
            else:
                # The first result of the transaction will be the local part of
                # the VM to destroy.
                return objects.NodeID(machine = vmfactory_id.machine,
                    local = int(result[0]))

            try:
                result = self._redis.transaction(check_clean,
                    clean_vm_count_key, vmfactory_key)
            except _Return as e:
                # The check_dirty function raises _Return(None) if we should
                # *not* start creating a new virtual machine.
                assert e.what is None
            else:
                # If the transaction didn't raise an exception, that means
                # everything went fine and we should signal to the VM
                # factory to begin creating a new VM.
                return True

            time.sleep(poll_every)

    def vmfactory_note_clean_id(self, vmfactory_id, clean_id, _hints = None):
        vmfactory_key = "NodeInfo/%s" % (vmfactory_id.serialize(), )

        def note_clean(pipe):
            # watch(vmfactory_key)

            vmfactory_json = pipe.get(vmfactory_key)
            if vmfactory_json is None:
                raise objects.IDNotRegistered(vmfactory_id)
            vmfactory = VMFactory.from_dict(
                galah.common.marshal.loads(vmfactory_json))

            if vmfactory.state != VMFactory.STATE_CREATING_NOID:
                raise objects.CoreError(
                    "vmfactory is not creating a virtual machine that does "
                    "not yet have an ID"
                )

            pipe.multi()

            vmfactory.state = VMFactory.STATE_CREATING
            vmfactory.vm_id = clean_id.serialize()
            pipe.set(vmfactory_key,
                galah.common.marshal.dumps(vmfactory.to_dict()))

        # This will raise an appropriate exception if any errors occur
        self._redis.transaction(note_clean, vmfactory_key)

        return True

    def vmfactory_finish(self, vmfactory_id, _hints = None):
        vmfactory_key = "NodeInfo/%s" % (vmfactory_id.serialize(), )

        clean_vm_queue_key = "CleanVMs/%s" % (
            vmfactory_id.machine.encode("utf_8"))

        def finish(pipe):
            # watch(vmfactory_key, clean_vm_queue_key)

            vmfactory_json = pipe.get(vmfactory_key)
            if vmfactory_json is None:
                raise objects.IDNotRegistered(vmfactory_id)
            vmfactory = VMFactory.from_dict(
                galah.common.marshal.loads(vmfactory_json))

            if vmfactory.state not in (VMFactory.STATE_CREATING,
                    VMFactory.STATE_DESTROYING):
                raise objects.CoreError("vmfactory not in correct state")

            vm_id = objects.NodeID.deserialize(vmfactory.vm_id)

            pipe.multi()

            if vmfactory.state == VMFactory.STATE_CREATING:
                pipe.lpush(clean_vm_queue_key,
                    unicode(vm_id.local).encode("utf_8"))

            vmfactory.state = VMFactory.STATE_IDLE
            vmfactory.vm_id = None
            pipe.set(vmfactory_key,
                galah.common.marshal.dumps(vmfactory.to_dict()))

        self._redis.transaction(finish, vmfactory_key, clean_vm_queue_key)

        return True


    # oooooo     oooo ooo        ooooo
    #  `888.     .8'  `88.       .888'
    #   `888.   .8'    888b     d'888   .oooo.o
    #    `888. .8'     8 Y88. .P  888  d88(  "8
    #     `888.8'      8  `888'   888  `"Y88b.
    #      `888'       8    Y     888  o.  )88b
    #       `8'       o8o        o888o 8""888P'

    def vm_register(self, vm_id, _hints = None):
        # We only add an entry in the NodeSet and not in NodeInfo because an
        # empty hash field cannot be created.
        rv = self._redis.sadd(
            "NodeSet/VM/%s" % (vm_id.machine.encode("utf_8"), ),
            str(vm_id.local)
        )
        return rv == 1

    def vm_unregister(self, vm_id, _hints = None):
        # We need to be careful to make sure to delete both the NodeInfo entry
        # for the VM as well as the NodeSet entry. We use a "pipeline" to make
        # the two deletions atomic in the unlikely event of an application
        # failure between sending the two commands.
        with self._redis.pipeline() as pipe:
            pipe.srem("NodeSet/VM/%s" % (vm_id.machine.encode("utf_8"), ),
                str(vm_id.local))
            pipe.delete("NodeInfo/%s" % (vm_id.serialize(), ))

            srem_rv, del_rv = pipe.execute()
            return srem_rv == 1

    def vm_set_metadata(self, vm_id, key, value, _hints = None):
        if not isinstance(key, unicode):
            raise TypeError("key must be unicode string, got %r." % (key, ))
        if not isinstance(value, str):
            raise TypeError("value must be str, got %r." % (value, ))

        # We do the set in a formal transaction so that we can ensure that the
        # vm isn't deleted right before we set its metadata.
        vm_set_key = "NodeSet/VM/%s" % (vm_id.machine.encode("utf_8"), )
        vm_info_key = "NodeInfo/%s" % (vm_id.serialize(), )
        def set_metadata(pipe):
            # watch(vm_set_key)

            if pipe.sismember(vm_set_key, str(vm_id.local)) != 1:
                raise objects.IDNotRegistered(vm_id)

            # Following commands will be queued and executed at once
            pipe.multi()

            pipe.hset(vm_info_key, key.encode("utf_8"), value)

        # Only one command is executed in the multi block above so we can pull
        # it out easily here.
        rv = self._redis.transaction(set_metadata, vm_set_key)[0]
        return rv == 1

    def vm_get_metadata(self, vm_id, key, _hints = None):
        if not isinstance(key, unicode):
            raise TypeError("key must be unicode string, got %s." %
                (repr(key), ))

        vm_key = "NodeInfo/%s" % (vm_id.serialize(), )
        rv = self._redis.hget(vm_key, key.encode("utf_8"))
        return rv

    def vm_mark_dirty(self, vm_id, _hints = None):
        self._redis.lpush("DirtyVMs/%s" % (vm_id.machine.encode("utf_8"), ),
            str(vm_id.local))

        return True
