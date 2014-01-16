# internal
from galah.core.backends.redis import *

# test internal
from .redis_utils import parse_redis_config

# stdlib
import re

# external
import pytest
import redis

@pytest.fixture
def redis_server(request, capfd):
    raw_config = request.config.getoption("--redis")
    if not raw_config:
        pytest.skip("Configuration with `--redis` required for this test.")
    config = parse_redis_config(raw_config)

    db = config.db_range[0]
    connection = redis.StrictRedis(host = config.host, port = config.port,
        db = db)

    # Ensure that nobody else is using the database, this is a failsafe to
    # prevent inadvertantly deleting a production database.
    assert len(connection.client_list()) != 1

    # This will delete everything in the current database
    connection.flushdb()

    return connection

class TestRedis:
    def test_foo(self, redis_server):
        redis_server.ping()

        assert False
