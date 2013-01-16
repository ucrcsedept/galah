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

from galah.base.prioritydict import PriorityDict
from collections import namedtuple
from galah.base.flockmail import InternalTestRequest
import datetime

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("shepherd")

import heapq
class FlockManager:
	__slots__ = ("_flock", "_bleet_queue", "_working_queue")

	SheepInfo = namedtuple("SheepInfo", ["environment", "servicing_request"])

	def __init__(self, match_found):
		# The flock of sheep we are managing. Dictionary mapping sheep
		# identities to information on that sheep (specifically SheepInfo
		# instances).
		self._flock = {}

		# A priority queue where sheep are ordered by the time when they last
		# bleeted. The top of/smallest item in the priority queue is the sheep
		# who has bleeted the farthest amount of time ago.
		self._bleet_queue = PriorityDict()

		# A priority queue that keeps track of how long each sheep has been
		# working on their current request. Same idea as the bleet queue.
		self._service_queue = PriorityDict()

		# A priority queue that keeps track of how long each request has been
		# waiting for a match. Same idea as the bleet queue.
		self._request_queue = PriorityDict()

		# A function that's called whenever a sheep is paired with a particular
		# test request.
		self.match_found = match_found

	def _dispatch_match_found(self, sheep_identity, request):
		if self.match_found(self, sheep_identity, request):
			del self._request_queue[request]
			return True

		return False

	def _sheep_available(self, identity):
		"""Called internally whenever a new sheep becomes available."""

		sheep_environment = self._flock[identity]

		for i in self._request_queue.keys()[:]:
			if FlockManager.check_environments(i.environment, \
					sheep_environment):
				if self._dispatch_match_found(identity, i):
					break

	def received_request(self, request):
		"""Called externally whenever a test request has arrived."""

		assert isinstance(request, InternalTestRequest)

		self._request_queue[request] = datetime.datetime.now()

		# Go through every available sheep and check to see if a match exists
		for i in self._bleet_queue.keys():
			if FlockManager.check_environments(request.environment,
					self._flock[i].environment):
				if self._dispatch_match_found(i, request):
					break

	def manage_sheep(self, identity, environment):
		"""
		Tell the flock manager to keep track of the given sheep. Returns True if
		the sheep has not previously been added. Returns False if the sheep was
		already known by the manager.

		Calls sheep_bleeted on the sheep as well.

		"""

		if identity in self._flock:
			return False

		if not isinstance(environment, dict):
			raise TypeError("environment must be a dict.")

		self._flock[identity] = FlockManager.SheepInfo(environment, None)

		self.sheep_bleeted(identity)

		return True

	def remove_sheep(self, identity):
		if identity not in self._flock:
			raise ValueError("No sheep with given identity.")

		del self._flock[identity]

		if identity not in self._bleet_queue:
			del self._bleet_queue[identity]

		if identity not in self._service_queue:
			del self._service_queue[identity]

	def sheep_bleeted(self, identity):
		"""
		Should be called whenever a sheep bleets. Will return True if all is
		well, will return False if the sheep is not recognized and do nothing.

		"""

		if identity not in self._flock:
			return False

		newly_available = identity not in self._bleet_queue

		self._bleet_queue[identity] = datetime.datetime.now()

		if newly_available:
			self._sheep_available(identity)

		return True

	def assign_sheep(self, identity, request):
		"""Assigns a particular request to a sheep."""

		assert request in self._request_queue
		assert identity in self._bleet_queue

		# Delete the sheep and request from their respective queues
		del self._request_queue[request]
		del self._bleet_queue[identity]

		# Make note of when the sheep started on the request
		self._service_queue[identity] = datetime.datetime.now()

		self._flock.servicing_request = request

	@staticmethod
	def check_environments(a, b):
		"""
		Will return true if a is a subset of b.
		> environments_match({"compiler": "g++"}, {"os": "unix", "compiler": "g++"})
		True
		> environments_match({"os": "unix", "compiler": "g++"}, {"compiler": "g++"})
		False

		"""

		return all(
			k in b and b[k] == v for k, v in a.items()
		)

	# def cleanup(self, bleet_timeout = None, service_timeout = None):
	# 	"""
	# 	Returns two lists in a tuple where the first list is any sheep who timed
	# 	out due to bleets, and the second list is any sheep that timed out while
	# 	servicing a request.

	# 	"""
	
	# 	lost_sheep = []
	# 	killed_sheep = []

	# 	if bleet_timeout and self._bleet_queue:
	# 		while (self._bleet_queue.smallest().priority <
	# 				datetime.datetime.now() -
	# 				datetime.timedelta(seconds = bleet_timeout)):
	# 			lost_sheep.append(self._bleet_queue.smallest().value)

	# 	if service_timeout and self._service_queue:
	# 		while (self._service_queue.smallest().priority <
	# 				datetime.datetime.now() -
	# 				datetime.timedelta(seconds = service_timeout)):
	# 			killed_sheep.append(self._service_queue.smallest().value)

	# 	return (lost_sheep, killed_sheep)
