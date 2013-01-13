# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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
        return """{"submission_id": "abdsfbsdb2342", "result": "applesauce"}"""