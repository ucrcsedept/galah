#!/usr/bin/python3

# Copyright 2011 John C. Sullivan
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

import subprocess
import configparser
import sys
import os
import argparse

if __name__ != "__main__":
    raise ImportError("This script cannot be imported.")
	
# Set up argument parser
argParser = argparse.ArgumentParser(description = "Control any of the Galah's Virtual Machines.")
argParser.add_argument("-c", "--config", help="Specify which configuration file to use.", dest="config_path")
argParser.add_argument("--create", help="Specify that a completely new virtual machine should be created.")
args = argParser.parse_args()

# Load up the configuration file parser
config = configparser.SafeConfigParser()

# Figure out the possible places for the configuration file to be
configFilePaths = []
if args.config_path == None:
    configFilePaths = ["%s.conf" % os.path.basename(sys.argv[0])]
else:
    configFilePaths = [args.config_path]

# Ensure that one of the configuraton files specifed exists. I know this
# method is frowned upon, however, if the file is modified much the same
# result will ensue when I try to access it in a later block (stderr
# will get printed to and the exit status will be set to 1). Thus I see
# no security hole.
foundConfigFile = False
for i in configFilePaths:
    if os.access(i, os.F_OK):
        foundConfigFile = True

if not foundConfigFile:
    print("Fatal Error: Could not find configuration file(s) at %s." % (", ".join(configFilePaths)), file=sys.stderr)
    sys.exit(1)

# Attempt to read the configuration file(s)
try:
    config.readfp(configFilePaths)
except:
    print("Fatal Error: Invalid configuration file(s) at %s." % (", ".join(configFilePaths)), file=sys.stderr)
    sys.exit(1)
    
# This will hold the compiled command to run
command = []
