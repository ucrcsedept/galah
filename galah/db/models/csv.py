from mongoengine import *

class CSV(Document):
    requester = StringField(required = True)
    file_location = StringField()
    error_string = StringField()
    expires = DateTimeField()

    meta = {
        "allow_inheritance": False
    }
