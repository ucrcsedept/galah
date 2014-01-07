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

# internal
import galah.core

log = logging.getLogger("galah.vmfactory")

def main():
    # Load Galah's configuration.
    from galah.base.config import load_config
    config = load_config("sheep")
    log.debug("Loaded configuration: %s", config)

    while True:
        # This will check if the VM factory crashed and will add any dirty VM
        # or clean VM to the deletion queue if they are associated with this
        # VM factory.
        if galah.core.vmfactory_repair(config["VMFACTORY_ID"]):
            log.warning("vmfactory crashed.")

        # This will block until either a dirty VM has been queued for deletion
        # or the number of clean VM's is less than the desired number. It will
        # then return either a dirty VM or some information that will be used
        # to create the clean VM. This vmfactory will also be associated with
        # clean or dirty VM to aid in crash recovery.
        dirty_vm, clean_vm = galah.core.vmfactory_grab(config["VMFACTORY_ID"])

        if dirty_vm is not None:
            log.info("Destroying virtual machine %s.", dirty_vm)
        elif clean_vm is not None:
            log.info("Destroying virtual machine %s.", clean_vm)

        # Mark the dirty or clean VM as successfully deleted/created and
        # disassociate it from this vmfactory.
        galah.core.vmfactory_finish_dirty(config["VMFACTORY_ID"])

if __name__ == "__main__":
    sys.exit(main())
