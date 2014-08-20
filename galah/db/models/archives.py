from mongoengine import *

class Archive(Document):
    requester = StringField(required = True)
    file_location = StringField()
    error_string = StringField()
    expires = DateTimeField()
    archive_type = StringField(choices = ["assignment_package", "single_submission"], required = True)
    

    meta = {
        "allow_inheritance": False
    }

