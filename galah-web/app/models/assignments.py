from mongoengine import *

from classes import Class

class TestDescription(EmbeddedDocument):
    title = StringField(required = True)
    description = StringField()
    
    meta = {
        "allow_inheritance": False
    }

class TestSpecification(EmbeddedDocument):
    testDriver = StringField(required = True)
    timeout = IntField(default = 30)
    actions = ListField(StringField())
    config = DictField()

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    forClass = ObjectIdField(required = True)
    
    # English description of each of the tests
    tests = ListField(EmbeddedDocumentField(TestDescription))
    
    # Rigid specification used by the shepherd to craft a test request
    testSpecification = EmbeddedDocumentField(TestSpecification, required = True)

    meta = {
        "allow_inheritance": False
    }
