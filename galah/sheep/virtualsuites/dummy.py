import time

# Performs one time setup for the entire module
def setup(logger):
    logger.debug("setup called. Doing nothing.")

class Producer:
	def __init__(self, logger):
		self.logger = logger

	def produce_vm(self):
		self.logger.debug("produce_vm called. Doing nothing.")
		time.sleep(10)
		return 0

class Consumer:
    def __init__(self, logger):
        self.logger = logger

    def prepare_machine(self):
        self.logger.debug("prepare machine called. Doing nothing.")
        time.sleep(10)
        return 0

    def run_test(self, container_id, test_request):
        self.logger.debug("run_test called. Doing nothing.")
        time.sleep(20)
        return {"_id": test_request["submission"]["id"], "tests": [{"message": "Could not find `main.cpp`.", "score": 0, "max_score": 1, "name": "File Name Correct"}, {"parts": [["Found Hello", 0, 0.5], ["Found World", 0, 0.5]], "score": 0, "max_score": 1, "name": "Found Hello World"}], "score": 0, "max_score": 2}
