class RigidDict(dict):
    class ValidationError(RuntimeError):
        def __init__(self, *args, **kwargs):
            RuntimeError.__init__(self, *args, **kwargs)
    
    def _get_fields(self, prev = None):
        if not prev: prev = set()
        
        return prev
    
    def __init__(self, *args, **kwargs):
        super(RigidDict, self).__init__(*args, **kwargs)
        
        self.validate()
        
    def validate(self):
        for k, v in vars(self).items():
            if k not in self._fields:
                raise ValidationError("Extraneous attribute '%s' found." % k)
                
    def __setitem__(self, key, value):
        if key not in self._get_fields():
            raise RigidDict.ValidationError("Invalid attribute '%s'." % key)
            
        super(RigidDict, self).__setitem__(key, value)
        

class TestResult(RigidDict):
    def _get_fields(self, prev = None):
        if not prev: prev = set()
        
        return super(TestResult, self)._get_fields(
            prev | {"name", "score", "maxScore", "message", "messages"}
        )
    
    def __init__(self, *args, **kwargs):
        super(TestResult, self).__init__(*args, **kwargs)
