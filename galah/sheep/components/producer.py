import logging
import galah.sheep.utility.universal as universal
from galah.sheep.utility.suitehelpers import get_virtual_suite
import Queue
import utility
import time

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sheep")

@universal.handleExiting
def run():
    """
    Constantly creates new virtual machines.
    
    """
    
    logger = logging.getLogger("galah.sheep.producer")
    
	# Initialize the correct producer based on the selected virtual suite.
    virtual_suite = get_virtual_suite(config["VIRTUAL_SUITE"])
    producer = virtual_suite.Producer(logger)

    logger.info("Producer is starting")
    
    # Loop until the program is shutting down
    while not universal.exiting:
        producer.produce_vm()
