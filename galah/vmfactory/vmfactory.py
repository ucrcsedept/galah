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

log = logging.getLogger("galah.vmfactory")

def main():
    con = galah.core.backends.redis.RedisConnection()

    # Load Galah's configuration. Don't load a namespace in preparation for
    # the newer config code.
    from galah.base.config import load_config
    config = load_config("")
    log.debug("Loaded configuration...\n%s", config)

    # Allocate an ID for ourselves
    my_id = con.node_allocate_id(config["core/MACHINE_ID"])

    # Register that ID with the backend
    con.vmfactory_register(my_id)

    while True:
        log.debug("Waiting for task...")
        task = con.vmfactory_grab(my_id)

        if task is True:
            log.info("Creating new virtual machine.")

        # Mark the dirty or clean VM as successfully deleted/created and
        # disassociate it from this vmfactory.
        con.vmfactory_finish(my_id)

if __name__ == "__main__":
    sys.stdin.close()

    sys.exit(main())
