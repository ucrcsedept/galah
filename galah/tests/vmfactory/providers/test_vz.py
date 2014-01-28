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
    def test_run_vzctl_smoke(self, vz):
        """A smoke test to make sure that ``vzctl`` is available."""

        assert vz._run_vzctl(["--version"]) == 0

    def test_get_containers_smoke(self, vz):
        """A smoke test to make sure that ``_get_containers`` doesn't error."""

        vz._get_containers(False)
        vz._get_containers(True)
