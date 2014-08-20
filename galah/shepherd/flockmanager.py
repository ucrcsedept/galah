from galah.base.prioritydict import PriorityDict
from collections import namedtuple
from galah.base.flockmail import InternalTestRequest
import datetime

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("shepherd")

import heapq
class FlockManager:
	class SheepInfo:
		__slots__ = ("environment", "servicing_request")

		def __init__(self, environment, servicing_request):
			self.environment = environment
			self.servicing_request = servicing_request

	def __init__(self, match_found, bleet_timeout, service_timeout):
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

		# The amount of time a sheep can go without bleeting before it is
		# assumed to be lost.
		self.bleet_timeout = bleet_timeout

		# The amount of time that a sheep may spend servicing a request before
		# it is assumed to be dead.
		self.service_timeout = service_timeout

		# A function that's called whenever a sheep is paired with a particular
		# test request.
		self.match_found = match_found

	def _dispatch_match_found(self, sheep_identity, request):
		if self.match_found(self, sheep_identity, request):
			self.assign_sheep(sheep_identity, request)

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

		if identity in self._bleet_queue:
			del self._bleet_queue[identity]

		if identity in self._service_queue:
			del self._service_queue[identity]

	IGNORE = "ignore"
	def sheep_bleeted(self, identity):
		"""
		Should be called whenever a sheep bleets. Will return True if all is
		well, will return False if the sheep is not recognized and do nothing.

		"""

		if not self.is_sheep_managed(identity):
			return False

		# If the sheep is listed as servicing a request, this bleet may have
		# come in before the shepherd sent the test request to the sheep, in
		# which case we just want to ignore the bleet.
		if identity in self._service_queue:
			return FlockManager.IGNORE

		# Check whether we're in the bleet queue before we add ourselves to
		# it.
		newly_available = identity not in self._bleet_queue

		self._bleet_queue[identity] = datetime.datetime.now()

		if newly_available:
			self._sheep_available(identity)

		return True

	def sheep_finished(self, identity):
		if identity not in self._service_queue:
			return False

		del self._service_queue[identity]
		self._flock[identity].servicing_request = None

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

		self._flock[identity].servicing_request = request

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

	def is_sheep_managed(self, identity):
		return identity in self._flock

	def cleanup(self):
		"""
		Returns two lists in a tuple where the first list is any sheep who timed
		out due to bleets (lost sheep), and the second list is any sheep that
		timed out while servicing a request (killed sheep).

		Any lost sheep will simply be forgotten about, any killed sheep will
		have the test request they were servicing placed back into the request
		queue than they will be forgotten about as well.

		"""

		lost_sheep = []
		killed_sheep = []

		# Find all the sheep who are not servicing requests but have not bleeted
		# in awhile.
		if self.bleet_timeout:
			while (self._bleet_queue and self._bleet_queue.smallest().priority <
					datetime.datetime.now() - self.bleet_timeout):
				lost_sheep.append(self._bleet_queue.pop_smallest().value)

		# Find all the sheep who have been servicing a single request too long.
		if self.service_timeout:
			while (self._service_queue and
					self._service_queue.smallest().priority <
					datetime.datetime.now() - self.service_timeout):
				killed_sheep.append(self._service_queue.pop_smallest().value)

		# Any lost sheep can simply be forgotten about as if they never existed.
		for i in lost_sheep:
			self.remove_sheep(i)

		# Any killed sheep needs to have the test request they were servicing
		# put back into the request queue again and then they need to be
		# forgotten.
		for i in killed_sheep:
			#self.received_request(self._flock[i].servicing_request)
			self.remove_sheep(i)

		return lost_sheep, killed_sheep
