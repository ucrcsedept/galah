from config import db
from mongoengine import *

from classes import Class
from testresults import TestResult

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    forClass = ReferenceField(Class, CASCADE, required = True)
    tests = ListField(ReferenceField(TestResult))

    meta = {
        "allow_inheritance": False
    }
