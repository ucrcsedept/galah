# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

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

