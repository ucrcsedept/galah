# Any module that implements pytest_addoption should be added here, otherwise
# py.test will not call the hook correctly at tool startup.
pytest_plugins = ("galah.tests.pytest_plugins.redis", )
