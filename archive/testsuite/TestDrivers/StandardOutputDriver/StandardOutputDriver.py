#!/cygdrive/c/python27/python.exe

"""
A fully conforming Galah Test Driver used to test a programs output given
certain inputs.
"""

# Requires AT LEAST python 2.6 for the json library. If you must use python
# 2.5 then you can use the simplejson library instead.

import sys, json, atexit, subprocessaio, threading, datetime
from cStringIO import StringIO

from Queue import Queue

global errors
errors = []
def exitDriver():
    """
    Ran when the program executes, mostly independent of the mode of execution.
    """
    json.dump(errors, sys.stderr)
    sys.stderr.write("\n")
    
def main(): 
    # Ensure proper JSON will be printed to stderr upon exit
    atexit.register(exitDriver)

    # Parse the input we get from the testing suite
    config = None
    try:
        config = json.load(sys.stdin)
    except ValueError as e:
        errors.append("Input Invalid: %s" % str(e))
        sys.exit()

    # Get all of the testables
    testables = config.get("testables", [])
    
    class Task:
        def __init__(self, zscript, zconfig, ztestables):
            # The script that needs to be executed
            self.script = zscript
            
            self.testables = ztestables
            
            # The configuration to send to the script's std. input
            self.config = zconfig
            
            
            # Will hold the script's standard output and input, respectively.
            self.stdout = StringIO()
            self.stderr = StringIO()
            
            # Will hold the process running the script
            self.proc = None
            
            # Will hold when proc was started
            self.startTime = None
            
            # Whether or not the task timed out
            self.timedOut = False
    
    # Go through all of the scripts and create a list of tasks we will need to
    # process.
    tasks = []
    for script in config.get("actions", []):
        # If no path was provided there's really nothing to do for this script.
        if "path" not in script:
            errors.append("Warning: No path given for script! Skipping.")
            continue
    
        # Load the script file's configuration if one is supplied
        testablesPerInstance = 1
        try:
            scriptConfigFile = json.load(open(script["path"] + ".conf"))
            
            testablesPerInstance = scriptConfigFile.get("testablesPerInstance",
                                                        1)
            if testablesPerInstance > 1:
                errors.append("Warning: Value of testablesPerInstance for "
                              "script configuration '%s' ignored. Defaulting to"
                              " 1." % script["path"])
        except ValueError as e:
            # Thrown by json.load if something happened.
            errors.append("Warning: Configuration file for script '%s' is "
                          "invalid, JSON could not be decoded. Caught "
                          "exception: '%s'" % (script["path"], str(e)))
        except IOError:
            # Thrown if the script's configuration file could not be found.
            # Since a configuration file is optional, don't do anything special.
            pass
    
        # testableGroups contains a list of lists (groups) where each group
        # will be provided to an instance of script. That instance will then
        # be expected to run tests on every testable in that group.
        # TODO: As of now, either a single instance will be given all tests, or
        # an instance will be created for every test. A middle ground should be
        # available
        testableGroups = None
        if testablesPerInstance == 0:
            testableGroups = [testables]
        else:
            testableGroups = [[i] for i in testables]
        
        for group in testableGroups:
            # Form the input that will be sent to the script
            scriptConfig = json.dumps({"tests": script["tests"],
                                       "info": script.get("info", {}),
                                       "testables": group})
            
            # Append a task
            tasks.append(Task(script["path"], scriptConfig, group))

    # Load up a new process for each task
    for i in tasks:
        i.proc = subprocessaio.Popen([i.script],
                                     stdin = subprocessaio.PIPE,
                                     stdout = subprocessaio.PIPE,
                                     stderr = subprocessaio.PIPE)
        
        i.startTime = datetime.datetime.now()
        
        # Write the configuration information to the new process's standard
        # output and then close stdin.
        i.proc.stdin.write(i.config)
        i.proc.stdin.close()
    
    # The amount of time it takes for a task to timeout
    scriptTimeout = datetime.timedelta(
        seconds = config.get("task_timeout", 30))

    keepRunning = True
    while keepRunning:
        # keepRunning will only be set to true again if a task is active
        keepRunning = False
        for i in tasks:
            # returncode is only set once a process exits, so were checking if
            # the task's process has ended already.
            if i.proc.returncode != None:
                continue
            
            keepRunning = True
            
            # Record the task's process's output
            i.stdout.write(i.proc.asyncread())
            i.stderr.write(i.proc.asyncread(stderr = True))
            
            # Check if the process is still running (and get the returnValue if
            # it stopped).
            returnValue = i.proc.poll()
            if returnValue != None:
                # TODO: Possibility that there is more in proccess's stdout and
                # stderr at this point, should provide a way to grab it all
                # dependably.
                continue
            
            # Check if the task has taken to long and kill it if it has.
            if datetime.datetime.now() - i.startTime > scriptTimeout:
                i.timedOut = True
                i.proc.kill()
    
    # Collect all the various lists of results that the harnesses output
    results = []
    failures = []
    for i in tasks:
        if i.timedOut:
            for testable in i.testables:
                failures.append({
                    "testable": testable,
                    "message": "Error: Test harness '%s' timed "
                               "out." % i.script})
            break
            
        i.stdout.seek(0)
        i.stderr.seek(0)
            
        print "stderr:", "\n".join(i.stderr.readlines())
        # Get the results from the test harness
        try:
            results += json.load(i.stdout)
        except ValueError:
            for testable in i.testables:
                failures.append({
                    "testable": testable,
                    "message": "Test harness '%s' gave invalid "
                               "output." % i.script})
                               
            errors.append("Error: Test harness '%s' gave invalid "
                          "output." % i.script)
        
        # Get the error output from the test harness, if this fails it's a
        # warning as opposed to an error.
        try:
            errors.append(json.load(i.stderr))
        except ValueError:
            errors.append("Warning: Test harness '%s' gave invalid "
                          "error output." % i.script)
            
    # Dump all the output from the test harnesses and peace out
    json.dump({"results": results, "errors": failures}, sys.stdout)
    sys.stdout.write("\n")
    
    return 0

if __name__ == "__main__":     
    exit(main())
