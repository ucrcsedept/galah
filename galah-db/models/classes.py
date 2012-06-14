from mongoengine import *

class Class(Document):
    name = StringField(required = True)
    instructors = StringField()
    website = URLField()

    meta = {
        "allow_inheritance": False
    }
