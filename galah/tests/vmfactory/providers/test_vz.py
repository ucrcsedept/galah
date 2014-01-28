# internal
from galah.vmfactory.providers.vz import *

# external
import pytest

@pytest.fixture
def vz(request):
    raw_config = request.config.getoption("--openvz")
    if not raw_config:
        pytest.skip("Configuration with `--openvz` required for this test.")
    config = eval(raw_config)

    return OpenVZProvider(**config)

class TestOpenVZProvider:
    def test_run_vzctl(self, vz):
        """
        A smoke test to make sure that ``vzctl`` and ``vzlist`` is available.

        """

        assert vz._run_vzctl(["--version"]) == 0
