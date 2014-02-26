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
from optparse import OptionParser, make_option

# galah external
from galah.core.objects import *
import galah.core.backends.redis

# internal
from galah.vmfactory.providers.vz import OpenVZProvider

log = logging.getLogger("galah.vmfactory")

# Parse the configuration file
from galah.base.config import load_config
config = load_config("")

def parse_arguments(args = sys.argv[1:]):
    option_list = [
        make_option(
            "--destroy-vms", action = "store_true", default = False,
            help =
                "If specified, the vmfactory will collect all galah-created "
                "VMs on the system and destroy them. This can be useful when "
                "changing VM templates or during testing. After destroying "
                "the VMs the VMFactory will exit."
        ),
        make_option(
            "--recover", action = "store_true", default = False,
            help =
                "If specified, the vmfactory will enter a recovery mode on "
                "startup where it will clear out all of the data on virtual "
                "machines that exist in the backend and try to rebuild it "
                "using local data."
        )
    ]

    parser = OptionParser(
        usage = "usage: %prog [options]",
        description =
            "Zips up a package and adds superzippy's super bootstrap logic to "
            "it. ENTRY POINT should be in the format module:function. Just "
            "like the entry_point option for distutils. Each PACKAGE string "
            "will be passed directly to pip so you may use options and expect "
            "normal results (ex: 'PyYAML --without-libyaml').",
        option_list = option_list
    )

    options, args = parser.parse_args(args)

    return (options, args)

def main(vmfactory_id, provider, con):
    while True:
        log.debug("Waiting for task...")
        task = con.vmfactory_grab(vmfactory_id)

        if isinstance(task, NodeID):
            log.debug("Destroying virtual machine %r.", task)

            # We don't expose the whole connection object to the destroy_vm
            # function and instead just give it a way to get metadata.
            get_metadata = lambda k: con.vm_get_metadata(task, k)

            provider.destroy_vm(task, get_metadata)

            # It's possible we'll fail between this command and the following
            # finish command, so the VM will go back into the dirty queue. This
            # is fine and should be picked up as an already-destroyed VM when
            # it's picked up again.
            con.vm_unregister(task)

            log.info("Destroyed virtual maching %r.", task)
        elif task is True:
            log.info("Creating new virtual machine.")

            # Create a new VM, we'll get any metadata associated with the VM
            # in the return value
            new_vm_metadata = provider.create_vm()
            log.debug("New VM created, not yet registered or prepared. "
                "Metadata: %r", new_vm_metadata)

            # Allocate a new ID for the VM
            new_vm_id = con.node_allocate_id(vmfactory_id.machine)

            # Register our new VM
            con.vm_register(new_vm_id)

            # Write all the metadata necessary
            for k, v in new_vm_metadata.items():
                con.vm_set_metadata(new_vm_id, k, v)

            # Note the ID of the VM before we try to prepare it
            con.vmfactory_note_clean_id(vmfactory_id, new_vm_id)
            log.debug("New VM created and registered with NodeID %r. Not yet "
                "prepared.", new_vm_id)

            # Prepare the VM
            get_metadata = lambda k: con.vm_get_metadata(new_vm_id, k)
            set_metadata = lambda k, v: con.vm_set_metadata(new_vm_id, k, v)
            provider.prepare_vm(new_vm_id, set_metadata, get_metadata)
            log.info("New VM prepared with NodeID %r.", new_vm_id)

        # Mark the dirty or clean VM as successfully deleted/created and
        # disassociate it from this vmfactory.
        con.vmfactory_finish(vmfactory_id)

def recover(vmfactory_id, provider, con, force_unregister):
    # Determine what other factories have been registered on this machine
    # already.
    registered_factories = con.vmfactory_list(vmfactory_id.machine)
    other_factories = set(registered_factories) - set([vmfactory_id])

    # Unregister the other factories or explode
    if other_factories:
        if force_unregister:
            log.warning("Other factories are registered, unregistering %r.",
                other_factories)
            for i in other_factories:
                con.vmfactory_unregister(i)
        else:
            log.error("Cannot start, other factories are registered.")
            raise RuntimeError("Cannot start, other factories are registered.")

    # We're going to assume we own the world now and completely recreate the
    # queue of dirty and clean virtual machines. This function will also give
    # us all the metadata our backend knows about each VM which will be useful
    # when trying to auth with the bootstrappers on each vm.
    metadata = con.vm_purge_all(vmfactory_id.machine)
    log.info("Cleared backend's VM information")

    clean_vms, dirty_vms = provider.recover_vms(metadata)

    print clean_vms, dirty_vms

    # Register all of the found virtual machines and set the appropriate meta
    # data
    clean_vm_ids, dirty_vm_ids = [], []
    def process_vms(metadata_list, id_list):
        for i in metadata_list:
            new_id = con.node_allocate_id(vmfactory_id.machine)
            con.vm_register(new_id)
            for k, v in i.items():
                con.vm_set_metadata(new_id, k.decode("utf_8"), v)

            id_list.append(new_id)
    process_vms(clean_vms, clean_vm_ids)
    process_vms(dirty_vms, dirty_vm_ids)

    # Mark the vms clean or dirty
    for i in clean_vm_ids:
        con.vm_mark_clean(i)
    for i in dirty_vm_ids:
        con.vm_mark_dirty(i)

if __name__ == "__main__":
    # We don't need anything from standard input so go ahead and close it
    sys.stdin.close()

    options, args = parse_arguments()

    # This will be an intermediate object at some point, but for now just
    # using the Redis connection directly is fine.
    con = galah.core.backends.redis.RedisConnection()

    # This will also be an intermediate object at some point, but it's fine
    # like this for now.
    provider = OpenVZProvider()

    # Allocate and register an ID for ourselves
    vmfactory_id = con.node_allocate_id(config["core/MACHINE_ID"])
    con.vmfactory_register(vmfactory_id)

    log.info("vmfactory starting with NodeID %r.", vmfactory_id)

    try:
        if options.recover:
            recover(vmfactory_id, provider, con, True)

        main(vmfactory_id, provider, con)
    finally:
        con.vmfactory_unregister(vmfactory_id)
