# We need to tell py.test to load our custom plugins
pytest_plugins = [
    "galah.tests.pytest_plugins.redis",
    "galah.tests.pytest_plugins.bootstrapper",
    "galah.tests.pytest_plugins.vz"
]
