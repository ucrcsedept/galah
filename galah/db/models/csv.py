# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from mongoengine import *

class CSV(Document):
    requester = StringField(required = True)
    file_location = StringField()
    error_string = StringField()
    expires = DateTimeField()

    meta = {
        "allow_inheritance": False
    }
