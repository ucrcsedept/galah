import subprocess, ConfigParser, sys, os, datetime
from galah.base.magic import memoize

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep/vz")

vzctlPath = "/usr/sbin/vzctl"
vzlistPath = "/usr/sbin/vzlist"
containerDirectory = None
nullFile = open("/dev/null", "w")

def check_call(*args, **kwargs):
    "Essentially subprocess.check_call. Added for compatibilty with <v2.5."

    returnValue = subprocess.call(*args, **kwargs)
    if returnValue != 0:
        raise SystemError((return_value, str(zparams[0])))
    else:
        return 0

def run_vzctl(zparams, timeout = config["VZCTL_RETRY_TIMEOUT"]):
    cmd = [vzctlPath] + zparams

    deadline = datetime.datetime.today() + timeout

    while True:
        return_value = subprocess.call(
            cmd, stdout = nullFile, stderr = nullFile
        )

        if return_value == 9 and datetime.datetime.today() < deadline:
            continue
        elif return_value != 0:
            raise SystemError((return_value, str(zparams[0])))
        else:
            return 0

@memoize
def find_container_directory(config_path = "/etc/vz/vz.conf"):
    """
    Finds the location of the container filesystems and returns it.

    config_path is the location of the OpenVZ configuration file.

    """

    # Load the vz configuration file to find out where the containers are
    # stored.
    vzconfig = ConfigParser.SafeConfigParser()
    try:
        vzconfig.readfp(FakeHeaderWrapper(open(config_path)))
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise IOError("Badly formed configuration file at %s."
                      % (config_path))
    except:
        raise IOError("Could not access OpenVZ configuration file at %s."
                      % (config_path))

    # Get the path to the directory container
    try:
        # The VE_PRIVATE key contains the location of the directory which houses
        # all of the root directorites of the VMs
        containerDirectory = vzconfig.get("global", "VE_PRIVATE")

        dirpath = containerDirectory.replace("$VEID", "")
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise IOError("Badly formed configuration file at %s."
                      % (config_path))

    return dirpath

# Hack to allow configparser to parse config files without section
# headers.
# Courtesy of http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
class FakeHeaderWrapper(object):
    def __init__(self, file, default_section = "global"):
        self.configFile = file
        self.sectionHeader = "[%s]\n" % default_section
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

def create_container(id_range = range(1, 255),
                    subnet = "10.0.1",
                    os_template = None,
                    description = None):
    """
    Calls vzctl create  to create a new OpenVZ container with an id in the
    given range. Iff an available id could not be found a RuntimeError is
    raised.

    The id of the newly created container is returned.

    This function blocks until the container is fully created.

    """

    # Get a set of all the extant containes
    containers = set(get_containers())

    # Find an available ID
    for i in id_range:
        if i not in containers:
            id = i
            break
    else:
        raise RuntimeError("Could not find availableVM ID in permissable range "
                           "[%s, %s]."
                           % (config.getint("CreateContainer", "idmin")))

    # Holds additional parameters that will be passed to vzctl create
    parameters = []

    if subnet != None:
        parameters += ["--ipadd", subnet + "." + str(id)]

    if os_template != None:
        parameters += ["--ostemplate", os_template]

    if description != None:
        parameters += ["--description", description]

    # Actually call vzctl to create the container
    run_vzctl(["create", str(id)] + parameters)

    return id

def start_container(id):
    "Starts a given container and raises a SystemError if it fails."

    run_vzctl(["start", str(id)])


def stop_container(id):
    "Stops a given container and raises a SystemError if it fails."

    run_vzctl(["stop", str(id)])

def destroy_container(id):
    "Destroys a given container and raises a SystemError if it fails."

    run_vzctl(["destroy", str(id)])

def extirpate_container(id):
    "Destroys a container and stops it first if it must."

    stop_container(id)
    destroy_container(id)

def inject_file(id, source, to, move = False, permissions = "rwx",
               unpack = False):
    """
    Injects a given file (source) from the host system into the filesystem of
    the container with id id at location to (to is an absolute filepath as
    seen by the container's filesystem.

    If source is a directory, all of the files inside of that directory will be
    injected, the directory itself will not be injected.

    If move is True, then the file will be moved, otherwise it will be
    copied.

    If unpack is True and source is a .tar or .tar.gz,
    the file source will be unpacked with the tar command into to, otherwise
    this option will be ignored. Iff move is True the package will be deleted
    after extracting.

    """

    # Figure out the fully qualified destination path as seen by the host
    # system
    ztoReal = container_to_host_path(id, to)

    # Use the system commands rather than python's filesystem functions for
    # efficiency and simplicity (we certainly know what system this code is
    # running on since OpenVZ only supports *nix).
    if unpack and source.endswith((".tar", ".tar.gz")):
        check_call(["tar", "-xzf", source, "-C", ztoReal],
                   stdout = nullFile, stderr = nullFile)
        if move:
            check_call(["rm", source], stdout = nullFile, stderr = nullFile)
    else:
        if os.path.isdir(source):
            files = [os.path.join(source, i) for i in os.listdir(source)]
        else:
            files = [source]

        if move:
            check_call(["mv", "-rf"] + files + [ztoReal],
                       stdout = nullFile, stderr = nullFile)
        else:
            check_call(["cp", "-rf"] + files + [ztoReal],
                       stdout = nullFile, stderr = nullFile)

    # Ensure that the permissions and owner are correct
    check_call(["chown", "-R", "0:0", ztoReal], stdout = nullFile, stderr = nullFile)
    check_call(["chmod", "-R", "a=%s" % (permissions), ztoReal],
               stdout = nullFile, stderr = nullFile)

def run_shell_script_from_host(id, script):
    """
    Runs the given script located at script on the host system inside of the
    running container (if the container is not yet running, it will be
    started). The script will be ran as root.

    Note: script MUST be a SHELL script located on the HOST system.

    """

    run_vzctl(["runscript", str(id), script])

def container_to_host_path(id, path):
    """
    Converts a path from the container's file system's perspective into a path
    from the host's file system's perspective.

    Note that path MUST be an absolute file path.

    """

    return os.path.join(find_container_directory(), str(id), path[1:])


def host_to_container_path(id, path):
    """
    Converts a path from the host's file system's perspective into a path
    from the container's file system's perspective.

    Note that path MUST be an absolute file path.

    """

    prefix = os.path.join(find_container_directory(), str(id))

    if not path.startswith(prefix):
        raise ValueError("path (%s) is not in the container" % path)

    return path[len(prefix):]

def run_script(id, script, interpreter = None):
    """
    Runs the given script located on the container's system inside of the
    running container (if the container is not yet running, it will be
    started). The script will be run as root.

    Note script must be the path as seen from the container's file system.

    """

    # Form the command
    command = ("" if interpreter == None else interpreter + " ")
    command += script

    execute(id, command, False)

def execute(id, code, block = True):
    """
    Runs the given code. Similar to runScript except that code is the script.

    """

    p = subprocess.Popen(
        [vzctlPath, "exec", str(id), "-"],
        stdin = subprocess.PIPE
        #stdout = nullFile,
        #stderr = nullFile
    )
    p.stdin.write(code)
    p.stdin.close()
    if block:
        p.wait()
        return p.returncode
    else:
        return

def set_attribute(id, attribute, value, save = True):
    """
    Sets the attribute attribute (only valid attributes are accepted,
    check documentation for vzctl set) to value on the given vm.

    If save is True, the attribute will persist when restarting the VM.

    """

    run_vzctl(["set", str(id), "--" + attribute, value] +
                    (["--save"] if save else ["--setmode", "ignore"]))

def get_attribute(id, attribute):
    p = subprocess.Popen([vzlistPath, "-Ho", attribute, str(id)],
                         stdout = subprocess.PIPE,
                         stderr = nullFile)

    output = p.communicate()

    if p.returncode != 0:
        raise SystemError((p.returncode,
                           "Could not get attribute %s of %s." %
                                (attribute, id)))

    return output[0].strip()

def get_containers(description_pattern = None):
    "Returns a list all of the extant containers."

    # If we do not care about the description, we can very quickly get a list
    # of the extant containers by enumerating through the directory which
    # contains the containers' private areas. Otherwise, we have to use
    # vzlist.
    if description_pattern == None:
        # Find the directory where the container's private areas are stored
        dirPath = find_container_directory()

        # Get all the containers that have already been created
        containers = []
        for i in os.listdir(dirPath):
            try:
                containers.append(int(i))
            except ValueError:
                pass

        return containers
    else:
        flags = ["-d", description_pattern]

        p = subprocess.Popen([vzlistPath] + flags + ["-aHo", "ctid"],
                             stdout = subprocess.PIPE, stderr = nullFile)

        output = p.communicate()

        if p.returncode != 0:
            raise SystemError((p.returncode, "Could not list containers"))

        return [int(i.strip()) for i in output[0].splitlines()]
