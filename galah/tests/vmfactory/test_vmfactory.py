# internal
from galah.vmfactory import vmfactory

# stdlib
import subprocess
import time
import sys
import inspect
import errno

# external
import pytest

# Parse the configuration file
from galah.base.config import load_config
config = load_config("")

# This configuration option comes up so much I give it a nicer name
my_machine = config["core/MACHINE_ID"]

import logging
log = logging.getLogger("galah.tests.vmfactory")

@pytest.fixture
def vmfactory_process(request, vz, redis_server):
    # Make sure no VM's exist on the system already
    log.info("Destroying all virtual machines.")
    for i in vz._get_containers(galah_created = True):
        log.info("Destroying container with CTID %r.", i)
        vz._destroy_container(i)

    # Wipe the redis database
    redis_server._redis.flushdb()

    vmfactory_processes = []
    def create_vmfactory(args = None):
        if args is None:
            args = []

        # Start up the vmfactory
        p = subprocess.Popen(
            [sys.executable, inspect.getsourcefile(vmfactory)] + args)
        vmfactory_processes.append(p)

        # Make sure it doesn't die immediately
        time.sleep(0.2)
        assert p.poll() is None

        return p

    def cleanup():
        # Send a friendly terminate signal to each process
        for i in vmfactory_processes:
            try:
                i.terminate()
            except OSError as e:
                if e.errno == errno.ESRCH:
                    pass
                else:
                    raise

        # Wait for about a second to see if they die cleanly, otherwise destroy
        # them with a less friendly kill signal.
        for i in range(5):
            time.sleep(0.2)

            # If every process has exited...
            if all(j.poll() is not None for j in vmfactory_processes):
                break
        else:
            # At least one of the processes are still alive so send a kill
            # signal to each.
            for i in vmfactory_processes:
                try:
                    i.kill()
                except OSError as e:
                    if e.errno == errno.ESRCH:
                        pass
                    else:
                        raise

        # Destroy any virtual machines that still exist on the system
        for i in vz._get_containers(galah_created = True):
            vz._destroy_container(i)

    request.addfinalizer(cleanup)

    return create_vmfactory

class TestLiveInstance:
    def test_simple_creation(self, vmfactory_process, redis_server):
        # The list of clean vms should be empty to begin with
        assert not redis_server.vm_list_clean(my_machine)

        # Start a single vmfactory
        vmfactory_process()

        # The list of clean vms should be non-empty after the factory is
        # running for a little while.
        for i in range(45):
            time.sleep(1)
            if redis_server.vm_list_clean(my_machine):
                break
        else:
            pytest.fail("vmfactory did not create clean machine")

    def test_recover_clean(self, vmfactory_process, redis_server):
        assert not redis_server.vmfactory_list(my_machine)

        # Start a single vmfactory and wait for it to create a VM
        p = vmfactory_process()
        for i in range(45):
            time.sleep(1)
            if redis_server.vm_list_clean(my_machine):
                break
        else:
            pytest.fail("vmfactory did not create clean machine")

        # Kill the vmfactory
        p.kill()

        assert len(redis_server.vmfactory_list(my_machine)) == 1

        # Start a new vmfactory in recovery mode, because the other vmfactory
        # is still registered it should exit quickly.
        p = vmfactory_process(["--recover"])
        for i in range(5):
            time.sleep(1)
            if p.poll() is not None:
                break
        else:
            pytest.fail("vmfactory did not exit when other vmfactory was "
                "still registered (supposedly) before going into recovery "
                "mode.")

        # Start a new vmfactory in recovery mode but this time tell it to
        # unregister any still-registered vmfactories
        p = vmfactory_process(["--recover", "--force-unregister"])

        # We need to give the vmfactory time to unregister any vmfactories and
        # collect the clean VM's. It should be able to do this very quickly.
        time.sleep(5)

        # The vmfactory should unregister all other vmfactories
        assert len(redis_server.vmfactory_list(my_machine)) == 1

        # And bring back the clean VM(s). Here we just check to make sure the
        # queue isn't empty
        assert redis_server.vm_list_clean(my_machine)
