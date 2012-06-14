#!/usr/bin/python26

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

import subprocess, ConfigParser, sys, os

vzctlPath = "/usr/sbin/vzctl"
vzlistPath = "/usr/sbin/vzlist"
containerDirectory = None
nullFile = open("/dev/null", "w")

def check_call(*args, **kwargs):
    "Essentially subprocess.check_call. Added for compatibilty with <v2.5."

    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((returnValue, str(args[0])))
    else:
        return 0

def runVzctl(zparams):
    cmd = [vzctlPath] + zparams

    check_call(cmd, stdout = nullFile, stderr = nullFile)

def findContainerDirectory(zopenVzConfigPath = "/etc/vz/vz.conf"):
    """
    Finds the location of the container filesystems and returns it.

    zopenVzConfigPath is the location of the OpenVZ configuration file.

    """

    # Load the vz configuration file to find out where the containers are
    # stored.
    vzconfig = ConfigParser.SafeConfigParser()
    try:
        vzconfig.readfp(FakeHeaderWrapper(open(zopenVzConfigPath)))
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise IOError("Badly formed configuration file at %s."
                      % (zopenVzConfigPath))
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
        raise IOError("Badly formed configuration file at %s."
                      % (zopenVzConfigPath))

    return dirpath

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
        if self.sectionHeader != None:
            try:
                return self.sectionHeader
            finally:
                self.sectionHeader = None
        else:
            return self.configFile.readline()

def createContainer(zidRange = range(1, 255),
                    zsubnet = "10.0.1",
                    zosTemplate = None,
                    zdescription = None):
    """
    Calls vzctl create  to create a new OpenVZ container with an id in the
    given range. Iff an available id could not be found a RuntimeError is
    raised.

    The id of the newly created container is returned.

    This function blocks until the container is fully created.

    """
    
    # Get a set of all the extant containes
    containers = set(getContainers())

    # Find an available ID
    for i in zidRange:
        if i not in containers:
            id = i
            break
    else:
        raise RuntimeError("Could not find availableVM ID in permissable range "
                           "[%s, %s]."
                           % (config.getint("CreateContainer", "idmin")))

    # Holds additional parameters that will be passed to vzctl create
    parameters = []
    
    if zsubnet != None:
        parameters += ["--ipadd", zsubnet + "." + str(id)]
        
    if zosTemplate != None:
        parameters += ["--ostemplate", zosTemplate]
        
    if zdescription != None:
        parameters += ["--description", zdescription]

    # Actually call vzctl to create the container
    runVzctl(["create", str(id)] + parameters)

    return id

def startContainer(zid):
    "Starts a given container and raises a SystemError if it fails."

    runVzctl(["start", str(zid)])


def stopContainer(zid):
    "Stops a given container and raises a SystemError if it fails."

    runVzctl(["stop", str(zid)])

def destroyContainer(zid):
    "Destroys a given container and raises a SystemError if it fails."

    runVzctl(["destroy", str(zid)])
    
def extirpateContainer(zid):
    "Destroys a container and stops it first if it must."
    
    stopContainer(zid)
    destroyContainer(zid)

def injectFile(zid, zfrom, zto, zmove = True, zpermissions = "rwx",
               zunpack = False):
    """
    Injects a given file (zfrom) from the host system into the filesystem of
    the container with id zid at location zto (zto is an absolute filepath as
    seen by the container's filesystem.
    
    If zfrom is a directory, all of the files inside of that directory will be
    injected, the directory itself will not be injected.

    If zmove is True, then the file will be moved, otherwise it will be
    copied.
    
    If zunpack is True and zfrom is a .tar or .tar.gz,
    the file zfrom will be unpacked with the tar command into zto, otherwise
    this option will be ignored. Iff zmove is True the package will be deleted
    after extracting.

    """

    # Figure out the fully qualified destination path as seen by the host
    # system
    ztoReal = containerToHostPath(zid, zto)

    # Use the system commands rather than python's filesystem functions for
    # efficiency and simplicity (we certainly know what system this code is
    # running on since OpenVZ only supports *nix).
    if zunpack and zfrom.endswith((".tar", ".tar.gz")):
        check_call(["tar", "-xzf", zfrom, "-C", ztoReal],
                   stdout = nullFile, stderr = nullFile)
        if zmove:
            check_call(["rm", zfrom], stdout = nullFile, stderr = nullFile)
    else:
        if os.path.isdir(zfrom):
            files = [os.path.join(i, l) for i, j, k in os.walk(zfrom) for l in k]
        else:
            files = [zfrom]
        
        if zmove:
            check_call(["mv", "-rf"] + files + [ztoReal],
                       stdout = nullFile, stderr = nullFile)
        else:
            check_call(["cp", "-rf"] + files + [ztoReal],
                       stdout = nullFile, stderr = nullFile)

    # Ensure that the permissions and owner are correct
    check_call(["chown", "-R", "0:0", ztoReal], stdout = nullFile, stderr = nullFile)
    check_call(["chmod", "-R", "a=%s" % (zpermissions), ztoReal],
               stdout = nullFile, stderr = nullFile)

def runShellScriptFromHost(zid, zscript):
    """
    Runs the given script located at zscript on the host system inside of the
    running container (if the container is not yet running, it will be
    started). The script will be ran as root.

    Note: zscript MUST be a SHELL script located on the HOST system.

    """

    runVzctl(["runscript", str(zid), zscript])

def containerToHostPath(zid, zpath):
    """
    Converts a path from the container's file system's perspective into a path
    from the host's file system's perspective.

    Note that zpath MUST be an absolute file path.

    """

    return os.path.join(findContainerDirectory(), str(zid), zpath[1:])
   

def hostToContainerPath(zid, zpath):
    """
    Converts a path from the host's file system's perspective into a path
    from the container's file system's perspective.

    Note that zpath MUST be an absolute file path.

    """

    prefix = os.path.join(findContainerDirectory(), str(zid))

    if not zpath.startswith(prefix):
        raise ValueError("zpath (%s) is not in the container" % zpath)

    return zpath[len(prefix):]

def runScript(zid, zscript, zinterpreter = None):
    """
    Runs the given script located on the container's system inside of the
    running container (if the container is not yet running, it will be
    started). The script will be run as root.

    Note zscript must be the path as seen from the container's file system.

    """

    # Form the command
    command = ("" if zinterpreter == None else zinterpreter + " ")
    command += zscript

    execute(zid, command, False)

def execute(zid, zcode, zblock = True):
    """
    Runs the given code. Similar to runScript except that zcode is the script.

    """

    p = subprocess.Popen([vzctlPath, "exec", str(zid), "-"],
                         stdin = subprocess.PIPE)
                         #stdout = nullFile,
                         #stderr = nullFile)
    p.stdin.write(zcode)
    p.stdin.close()
    if zblock:
        p.wait()
        return p.returncode
    else:
        return

def setAttribute(zid, zattribute, zvalue, zsave = True):
    """
    Sets the attribute zattribute (only valid attributes are accepted,
    check documentation for vzctl set) to zvalue on the given vm.

    If zsave is True, the attribute will persist when restarting the VM.

    """

    runVzctl(["set", str(zid), "--" + zattribute, zvalue] +
                    (["--save"] if zsave else ["--setmode", "ignore"]))

def getAttribute(zid, zattribute):
    p = subprocess.Popen([vzlistPath, "-Ho", zattribute, str(zid)],
                         stdout = subprocess.PIPE,
                         stderr = nullFile)

    output = p.communicate()

    if p.returncode != 0:
        raise SystemError((p.returncode,
                           "Could not get attribute %s of %s." %
                                (zattribute, zid)))

    return output[0].strip()

def getContainers(zdescriptionPattern = None):
    "Returns a list all of the extant containers."

    # If we do not care about the description, we can very quickly get a list
    # of the extant containers by enumerating through the directory which
    # contains the containers' private areas. Otherwise, we have to use
    # vzlist.
    if zdescriptionPattern == None:
        # Find the directory where the container's private areas are stored
        dirPath = findContainerDirectory()

        # Get all the containers that have already been created
        containers = []
        for i in os.listdir(dirPath):
            try:
                containers.append(int(i))
            except ValueError:
                pass
                
        return containers
    else:
        flags = ["-d", zdescriptionPattern]

        p = subprocess.Popen([vzlistPath] + flags + ["-aHo", "ctid"],
                             stdout = subprocess.PIPE, stderr = nullFile)
        
        output = p.communicate()
        
        if p.returncode != 0:
            raise SystemError((p.returncode, "Could not list containers"))
        
        return [int(i.strip()) for i in output[0].splitlines()]
