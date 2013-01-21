class PreparedTestRequest:
	"A test request meant for consumption by a test harness."

	def __init__(self, raw_harness, raw_submission, testables_directory,
			harness_directory, suite_specific = {}):
		self.raw_harness = raw_harness
		self.raw_submission = raw_submission
		self.testables_directory = testables_directory
		self.harness_directory = harness_directory
		self.suite_specific = suite_specific

	def to_dict(self):
		result = {
			"raw_harness": self.raw_harness,
			"raw_submission": self.raw_submission,
			"testables_directory": self.testables_directory,
			"harness_directory"; self.harness_directory
		}

		assert all("/" in i for i in suite_specific)

		result.update(suite_specific)

		return result