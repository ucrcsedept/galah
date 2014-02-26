# internal
import galah.vmfactory.providers.vz as vzprovider

# stdlib
import os
import sys

# external
import pytest

@pytest.fixture
def vz(request):
    try:
        provider = vzprovider.OpenVZProvider()
    except:
        # TODO: This is a little too all-encompassing and could allow a syntax
        # error to simply be skipped.
        pytest.skip("Could not create OpenVZ provider.")

    if not os.path.exists(provider.vzctl_path):
        pytest.skip("Configured path of vzctl (%r) does not exist.",
            provider.vzctl_path)

    # The output of vzctl and any other commands are sent to the NULL_FILE
    # which is normally /dev/null. We want to actually see the output of these
    # commands instead, so we'll point NULL_FILE at stderr
    vzprovider.NULL_FILE = sys.stderr

    return provider
