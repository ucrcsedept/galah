def pytest_addoption(parser):
    parser.addoption("--redis", action = "store",
        help = "host:port:db_range, ex: localhost:99:0-4")

    parser.addoption("--openvz", action = "store",
        help = "Python dictionary with kwargs to OpenVZProvider")
