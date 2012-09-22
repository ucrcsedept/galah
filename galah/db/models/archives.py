from mongoengine import *

class Archive(Document):
    requester = StringField(required = True)
    file_location = StringField()
    error_string = StringField()
    expires = DateTimeField()
    
    meta = {
        "allow_inheritance": False
    }

