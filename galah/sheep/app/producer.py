# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

import logging, universal, Queue, utility, pyvz, time

@universal.handleExiting
def run():
    """
    Constantly creates new containers until the container queue is full.
    
    """
    
    log = logging.getLogger("galah.sheep.producer")
    
    log.info("Producer is starting")
    
    # Get a list of all of the clean virtual machines that already exist
    cleanMachines = pyvz.getContainers("galah-vm: clean")
    
    # Add all the clean VMs to the queue
    for m in cleanMachines:
        utility.enqueue(universal.containers, m)
        
        log.info("Reusing clean VM with CTID %d" % m)
    
    # Loop until the program is shutting down
    while utility.waitForQueue(universal.containers):
        log.debug("Creating new VM")
        
        try:
            # Create new container with unique id
            id = pyvz.createContainer(
                    zosTemplate = universal.cmdOptions.ostemplate,
                    zdescription = "galah-vm: clean")
        except (RuntimeError, SystemError):
            log.exception("Error occured when creating VM")
            
            # Sleep for a bit and then try again
            time.sleep(5)
            continue
            
        log.debug("Created new VM with CTID %d" % id)
        
        try:
            # Start container
            pyvz.startContainer(id)
        except SystemError:
            log.exception("Could not start VM with CTID %d" % id)
            
            # If I keep trying to create VMs and starting them and it keeps
            # failing I may end up with hundreds of broken virtual machines
            # bogging down my server. I could add somewhat sophisticated
            # cleanup code ehre but this seems to be such a vital error that
            # shutting down is a reasonable option.
            log.critical("Cannot recover from non-starting VM")
            
            raise utility.exit()
        
        
        # Try to add the container to the queue until successful or the program
        # is exiting.
        utility.enqueue(universal.containers, id)
                
        log.debug("Added VM with CTID %d to the queue" % id)

