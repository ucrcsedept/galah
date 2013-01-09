# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

from mongoengine import *
import datetime

class TestDescription(EmbeddedDocument):
    title = StringField(required = True)
    description = StringField()
    
    meta = {
        "allow_inheritance": False
    }

class TestSpecification(EmbeddedDocument):
    test_driver = StringField(required = True)
    timeout = IntField(default = 30)
    actions = ListField(StringField())
    config = DictField()
    
    meta = {
        "allow_inheritance": False
    }

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    due_cutoff = DateTimeField()
    hide_until = DateTimeField(default = datetime.datetime.min, required = True)
    for_class = ObjectIdField(required = True)
    
    # English description of each of the tests
    tests = ListField(EmbeddedDocumentField(TestDescription))
    
    # Rigid specification used by the shepherd to craft a test request
    test_specification = EmbeddedDocumentField(TestSpecification)

    meta = {
        "allow_inheritance": False
    }

    def validate(self):
        if self.due_cutoff and self.due > self.due_cutoff:
            raise ValidationError("due cannot be later than due_cutoff")

        return Document.validate(self)