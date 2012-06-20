from mongoengine import *

class Class(Document):
    name = StringField(required = True)

    meta = {
        "allow_inheritance": False
    }
