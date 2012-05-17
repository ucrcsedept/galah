from bson import objectid.ObjectId

class SuiteConfiguration:
    def __init__(self):
        # List of pahts, each one pointing to a testable (relative paths only)
        self.testables = []
        
        # List of driver defined actions to take (ex: test harnesses to
        # execute). Each element may be any valid JSON object (so lists,
        # objects/dictionaries, numbers, strings...).
        self.actions = []
        
        # An object containing driver defined configuration data.
        self.config = {}

class TestRequest:
    def __init__(self):
        # The location of the testable archive in the Mongo Database.
        self.testableId = ObjectId()
        
        # The SuiteConfiguration to send the Testing Suite when it's run.
        self.suiteConfiguration = SuiteConfiguration()
