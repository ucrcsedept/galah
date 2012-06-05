from mongoengine import *

from classes import Class

class TestDescription(EmbeddedDocument):
    title = StringField(required = True)
    description = StringField()
    
    meta = {
        "allow_inheritance": False
    }

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    forClass = ObjectIdField(required = True)
    tests = ListField(EmbeddedDocumentField(TestDescription))

    meta = {
        "allow_inheritance": False
    }
