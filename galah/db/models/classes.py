# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from mongoengine import *

class Class(Document):
    name = StringField(required = True)

    meta = {
        "allow_inheritance": False
    }
