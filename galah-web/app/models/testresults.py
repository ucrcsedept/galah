from config import db

from mongoengine import *

class SubTest(EmbeddedDocument):
    score = FloatField()
    maxScore = FloatField()
    message = StringField()
    messages = ListField(StringField)

    meta = {
        "allow_inheritance": False
    }

class TestResult(Document):
    timestamp = DateTimeField(required = True)
    subTests = ListField(EmbeddedDocumentField(SubTest))
    score = FloatField()
    maxScore = FloatField()
    
    meta = {
        "allow_inheritance": False
    }
