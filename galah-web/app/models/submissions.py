from mongoengine import *

from assignments import Assignment
from users import User

class SubTest(EmbeddedDocument):
    score = FloatField()
    maxScore = FloatField()
    message = StringField()
    messages = ListField(StringField)

    meta = {
        "allow_inheritance": False
    }

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
