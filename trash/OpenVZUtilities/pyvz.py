#!/usr/local/bin/python3

# Copyright 2012 John C. Sullivan
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
import ConfigParser
import sys
import os

# Hack to allow configparser to parse config files without section
# headers.
# Courtesy of http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
class FakeHeaderWrapper(object):
    def __init__(self, zfile, zdefaultSection = "global"):
        self.configFile = zfile
        self.sectionHeader = "[%s]\n" % zdefaultSection
    def __iter__(self):
        return self
    def __next__(self):
        if self.sectionHeader != None:
            try:
                return self.sectionHeader
            finally:
                self.sectionHeader = None
        else:
            temp = self.configFile.readline()
            if temp == "":
                raise StopIteration
            return temp
    def readline(self):
        return self.configFile.readline()

def createOpenVZContainer(zopenVzConfigPath = "/etc/vz/vz.conf",
                          zidRange = range(2, 255)):
    # Load the vz configuration file to find out where the containers are
    # stored.
    vzconfig = ConfigParser.SafeConfigParser()
    try:
        vzconfig.readfp(FakeHeaderWrapper(open(zopenVzConfigPath)))
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise IOError("Badly formed configuration file at %s. Option "
                      "CreateContainer.vzconfig is required."
                      % (zopenVzConfigPath)
    except:
        raise IOError("Could not access OpenVZ configuration file at %s."
                      % (zopenVzConfigPath))

    # Get the path to the directory container
    try:
        # The VE_PRIVATE key contains the location of the directory which houses
        # all of the root directorites of the VMs
        containerDirectory = vzconfig.get("global", "VE_PRIVATE")
        
        dirpath = containerDirectory.replace("$VEID", "")
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # Guess at where the directory is (if the guess is wrong an exception
        # should occur later on).
        dirpath = "/vz/private"

    # Get all the containers that have already been created
    containers = None
    containers = set(os.listdir(dirpath))

    # Find an available id
    id = None
    for i in zidRange:
        if str(i) not in containers:
            id = i
            break

    # If no id was found, error.
    if id == None:
        raise RuntimeError("Could not find availableVM ID in permissable range "
                           "[%s, %s]."
                           % (config.getint("CreateContainer", "idmin")))
