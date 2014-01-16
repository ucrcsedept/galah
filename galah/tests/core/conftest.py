# stdlib
import inspect

# tests internal
from .redis_utils import RedisMonitor, parse_redis_config

# external
import pytest

def pytest_runtest_call(item):
    using_redis = "redis_server" in inspect.getargspec(item.function).args

    if using_redis:
        raw_config = item.config.getoption("--redis")
        if not raw_config:
            pytest.skip("Configuration with `--redis` required for this test.")
        config = parse_redis_config(raw_config)

        # Start the Redis monitor so we can see what commands get run.
        monitor = RedisMonitor(host = config.host, port = config.port,
            db = config.db_range[0])

    try:
        item.runtest()
    finally:
        if using_redis:
            monitor.stop()
