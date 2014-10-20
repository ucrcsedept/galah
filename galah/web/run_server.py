#!/usr/bin/env python

import logging
import sys

def setup_debug_logging():
    logger_galah = logging.getLogger("galah")
    logger_galah.setLevel(logging.DEBUG)

    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(logging.Formatter(
        "[%(levelname)s;%(name)s;%(asctime)s]: %(message)s"
    ))
    logger_galah.addHandler(streamhandler)

def main():
    from galah.web import app
    app.run()

if __name__ == "__main__":
    if "--quiet" not in sys.argv:
        setup_debug_logging()

    main()
