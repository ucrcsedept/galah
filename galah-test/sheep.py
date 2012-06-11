# Copyright 2012 John C. Sullivan, and Benjamin J. Kellogg
# 
# This file is part of Galah.
# 
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Galah. If not, see <http://www.gnu.org/licenses/>.

import zmq, threading, Queue, logging, sys, copy, os, app.maintainer, \
       app.universal, app.pyvz, signal, time

## Parse Command Line Arguments ##
from optparse import OptionParser, make_option

optionList = [
    make_option("--shepherd-port", dest = "shepherdPort", default = 6667,
                metavar = "PORT", type = "int",
                help = "Connect to shepherd on port PORT (default: %default)"),
                
    make_option("-s", "--shepherd-address", dest = "shepherdAddress",
                default = "localhost", metavar = "ADDRESS",
                help = "Connect to shepherd at address ADDRESS (default: "
                       "%default)"),
                
    make_option("--vm-port", dest = "vmPort", default = 6668, metavar = "port",
                type = "int",
                help = "Connect to virtual machine on port PORT (default: "
                       "%default)"),
    
    make_option("--vm-address", dest = "vmAddress", default = 6668,
                metavar = "ADDRESS",
                help = "Connect to virtual machine at address ADDRESS "
                       "(default: %default)"),

    make_option("--destroy-all", dest = "destroyAllMachines", default = False,
                action = "store_true",
                help = "Destroy all virtual machines ever started by this "
                       "script. Can be used with --leavedirty to destroy only "
                       "clean virtual machines."),
                       
    make_option("--leave-dirty", dest = "leaveDirtyMachines", default = False,
                action = "store_true",
                help = "Do not destroy any dirty virtual machines."),
    
    make_option("--nconsumers", dest = "nconsumers", default = 2,
                metavar = "NUM", type = "int",
                help = "NUM consumer threads will start and process test "
                       "requests."),

    make_option("--clean", dest = "clean", default = False,
                action = "store_true",
                help = "Only destroy virtual machines per the --destroy-all "
                       "and --leave-dirty options, do not produce any virtual "
                       "machines or consume any test requests."),

    make_option("--no-reuse", dest = "noReuse", default = False,
                action = "store_true",
                help = "Do not use any extant clean virtual machines. Note "
                       "this option does not destroy those machines."),

    make_option("-l", "--log-level", dest = "logLevel", type = "int",
                default = logging.DEBUG, metavar = "LEVEL",
                help = "Only output log entries above LEVEL (default: "
                       "%default)"),

    make_option("-q", "--quiet", dest = "verbose", action = "store_false",
                default = True,
                help = "Don't output logging messages to stdout"),

    make_option("-c", "--cache", dest = "nmachines", default = 1, type = "int",
                metavar = "NUM",
                help = "Number of virtual machines to automatically start "
                       "(default: %default)"),
                       
    make_option("--os-template", dest = "ostemplate",
                default = "centos-6-galah",
                help = "The OS template to pass to vzctl create when creating "
                       "the virtual machine (default: %defualt)"),

    make_option("--vm-subnet", dest = "vmSubnet", default = "10.0.1",
                help = "The subnet that the virtual machines will have their "
                       "addresses assigned in. For example, a vm with CTID 4 "
                       "will have ip address %default.4 given the default "
                       "value (default: %default)")
]
                  
parser = OptionParser(
    description = "Waits for test requests from the shepherd and executes them "
                  "in virutal machins that it creates. Must be run as a user "
                  "with access to vzctl.",
    version = "alpha-1",
    option_list = optionList)

app.universal.cmdOptions = parser.parse_args()[0]

from app.universal import cmdOptions

if cmdOptions.destroyAllMachines:
    cmdOptions.noReuse = True
    
if cmdOptions.logLevel == 0:
    cmdOptions.cmdOptions.verbose = False

## Root Check ##
# Note this isn't here for security, only convenience. If this wasn't here
# errors wouldn't start showing up until we started creating virtual machines.
if not os.geteuid() == 0:
    sys.exit("Only root can run this script")

## App-Wide Setup ##
app.universal.context = zmq.Context()
app.universal.containers = Queue.Queue(cmdOptions.nmachines)
    
if cmdOptions.verbose:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s.%(levelname)s: %(message)s"))
    topLog = logging.getLogger("galah")
    topLog.setLevel(cmdOptions.logLevel)
    topLog.addHandler(sh)

## Main ##
log = logging.getLogger("galah.sheep")

# All combinations of the two boolean values options.destroyAllMachines and
# options.leaveDirtyMachines are valid and do something distinct, thus
# there are four branches.
if cmdOptions.destroyAllMachines and cmdOptions.leaveDirtyMachines:
    # Only destroy clean VMs
    machinesToKill = app.pyvz.getContainers("galah-vm: clean")
elif cmdOptions.destroyAllMachines and not cmdOptions.leaveDirtyMachines:
    # Destroy everything!
    machinesToKill = app.pyvz.getContainers("galah-vm: *")
elif not cmdOptions.destroyAllMachines and \
     not cmdOptions.leaveDirtyMachines:
    # Only destroy dirty VMs (default)
    machinesToKill = app.pyvz.getContainers("galah-vm: dirty")
else: # not options.destroyAllMachines and not options.leaveDirtyMachines
    # Don't touch anything
    machinesToKill = []

# Kill all of the machines we need to kill
for m in machinesToKill:
    log.info("Destroying VM with CTID %d" % m)
    
    app.pyvz.extirpateContainer(m)

# Exit if that's all the user wanted us to do
if cmdOptions.clean:
    exit()

# Start the maintainer (who will start up the other threads)
maintainer = threading.Thread(target = app.maintainer.run,
                              args = (cmdOptions.nconsumers,),
                              name = "maintainer")
maintainer.start()

# Wait until we recieve a SIGINT (a hook was added by universal.py that changes
# exiting to True when a SIGINT is recieved)
try:
    while True:
        signal.pause()
except KeyboardInterrupt:    
    app.universal.exiting = True

# TODO: When zmq's queues have items in them still the program won't exit. This
# is that problem you (John) went onto freenode for help and solved. The
# solution is in your head somewhere....

log.info("Exiting...")
