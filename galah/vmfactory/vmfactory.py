#!/usr/bin/env python

# Copyright 2012-2014 Galah Group LLC
# Copyright 2012-2014 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

# stdlib
import sys
import logging

# galah external
from galah.core.objects import *
import galah.core.backends.redis

# internal
from galah.vmfactory.providers.vz import OpenVZProvider

log = logging.getLogger("galah.vmfactory")

# Parse the configuration file
from galah.base.config import load_config
config = load_config("")

machine_id = config["core/MACHINE_ID"]

def main(vmfactory_id, con):
    # This will also be an intermediate object at some point, but it's fine
    # like this for now.
    provider = OpenVZProvider()

    while True:
        log.debug("Waiting for task...")
        task = con.vmfactory_grab(vmfactory_id)

        if isinstance(task, NodeID):
            log.info("Destroying virtual machine %r.", task)

            # We don't expose the whole connection object to the destroy_vm
            # function and instead just give it a way to get metadata.
            get_metadata = lambda k: con.vm_get_metadata(task, k)

            provider.destroy_vm(task, get_metadata)

            # It's possible we'll fail between this command and the following
            # finish command, so the VM will go back into the dirty queue. This
            # is fine and should be picked up as an already-destroyed VM when
            # it's picked up again.
            con.vm_unregister(task)
        elif task is True:
            log.info("Creating new virtual machine.")

            # Create a new VM, we'll get any metadata associated with the VM
            # in the return value
            new_vm_metadata = provider.create_vm()
            log.debug("New VM created, not yet registered or prepared. "
                "Metadata: %r", new_vm_metadata)

            # Allocate a new ID for the VM
            new_vm_id = con.node_allocate_id(machine_id)

            # Register our new VM
            con.vm_register(new_vm_id)

            # Write all the metadata necessary
            for k, v in new_vm_metadata.items():
                con.vm_set_metadata(new_vm_id, k, v)

            # Note the ID of the VM before we try to prepare it
            con.vmfactory_note_clean_id(vmfactory_id, new_vm_id)
            log.info("New VM created and registered with NodeID %r. Not yet "
                "prepared.", new_vm_id)

            # Prepare the VM
            get_metadata = lambda k: con.vm_get_metadata(new_vm_id, k)
            set_metadata = lambda k, v: con.vm_set_metadata(new_vm_id, k, v)
            provider.prepare_vm(new_vm_id, set_metadata, get_metadata)
            log.info("New VM prepared.")

        # Mark the dirty or clean VM as successfully deleted/created and
        # disassociate it from this vmfactory.
        con.vmfactory_finish(vmfactory_id)

if __name__ == "__main__":
    # We don't need anything from standard input so go ahead and close it
    sys.stdin.close()

    # This will be an intermediate object at some point, but for now just
    # using the Redis connection directly is fine.
    con = galah.core.backends.redis.RedisConnection()

    # Allocate and register an ID for ourselves
    vmfactory_id = con.node_allocate_id(machine_id)
    con.vmfactory_register(vmfactory_id)

    log.info("vmfactory starting with NodeID %r.", vmfactory_id)

    try:
        main(vmfactory_id, con)
    finally:
        con.vmfactory_unregister(vmfactory_id)
