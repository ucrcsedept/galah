class PreparedTestRequest:
	"A test request meant for consumption by a test harness."

	def __init__(self, raw_harness, raw_submission, raw_assignment,
			testables_directory, harness_directory, suite_specific = {}):
		self.raw_harness = raw_harness
		self.raw_submission = raw_submission
		self.raw_assignment = raw_assignment
		self.testables_directory = testables_directory
		self.harness_directory = harness_directory
		self.suite_specific = suite_specific
		self.actions = []

	def to_dict(self):
		result = {
			"raw_harness": self.raw_harness,
			"raw_submission": self.raw_submission,
			"raw_assignment": self.raw_assignment,
			"testables_directory": self.testables_directory,
			"harness_directory": self.harness_directory,
			"actions": self.actions
		}

		assert all("/" in i for i in self.suite_specific)

		result.update(self.suite_specific)

		return result

	def update_actions(self, request_type = None):
		if request_type is None:
			request_type = self.raw_submission["test_type"]

			if not request_type:
				request_type = "public"

		if request_type == "public":
			grab_types = ("public", )
		elif request_type == "final":
			grab_types = ("public", "final")
		else:
			raise ValueError("Expected final or public, got %s." % request_type)

		self.actions = []
		for i in grab_types:
			self.actions += \
				self.raw_harness["config"].get("galah/actions", {}).get(i, [])