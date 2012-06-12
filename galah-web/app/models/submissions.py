from mongoengine import *

def rigidDocument(zdocClass):
    def validate(self, *zargs, **zkwargs):
        for k, v in vars(self).items():
            if k.startswith("_"): continue
            
            if k not in self._fields:
                raise ValidationError("Extraneous attributes were found.")
        
        return super(zdocClass, self).validate(*zargs, **zkwargs)

    zdocClass.validate = validate
    
    return zdocClass
        
@rigidDocument
class SubTest(EmbeddedDocument):
    name = StringField(required = True)
    score = FloatField()
    maxScore = FloatField()
    message = StringField()
    messages = ListField(StringField)

    meta = {
        "allow_inheritance": False
    }

@rigidDocument
class TestResult(EmbeddedDocument):
    subTests = ListField(EmbeddedDocumentField(SubTest))
    score = FloatField()
    maxScore = FloatField()
    
    meta = {
        "allow_inheritance": False
    }

class Submission(Document):
    assignment = ObjectIdField(required = True)
    user = StringField(required = True)
    timestamp = DateTimeField(required = True)
    testables = StringField(required = True)
    testResult = EmbeddedDocumentField(TestResult)
    
    meta = {
        "allow_inheritance": False
    }
