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

#def rigidDocument(zdocClass):
    #def validate(self, *zargs, **zkwargs):
        #for k, v in vars(self).items():
            #if k.startswith("_"): continue
            
            #if k not in self._fields:
                #raise ValidationError("Extraneous attributes were found.")
        
        #return super(zdocClass, self).validate(*zargs, **zkwargs)

    #zdocClass.validate = validate
    
    #return zdocClass
        
#@rigidDocument
#class SubTest(EmbeddedDocument):
    #name = StringField(required = True)
    #score = FloatField()
    #max_score = FloatField()
    #message = StringField()
    #messages = ListField(StringField)

    #meta = {
        #"allow_inheritance": False
    #}

#@rigidDocument
#class TestResult(EmbeddedDocument):
    #sub_tests = ListField(EmbeddedDocumentField(SubTest))
    #score = FloatField()
    #max_score = FloatField()
    
    #meta = {
        #"allow_inheritance": False
    #}

import os.path

# Load up the configuration so we know where the submission directory is
from galah.base.config import load_config
config = load_config("global")

class Submission(Document):
    assignment = ObjectIdField(required = True)
    user = StringField(required = True)
    timestamp = DateTimeField(required = True)
    marked_for_grading = BooleanField()
    most_recent = BooleanField()
    
    # Each filename should be a path relative to the root of the archive they
    # uploaded if they uploaded an archive, otherwise each filename should be
    # just the filename. Include extensions.
    uploaded_filenames = ListField(StringField())
    
    meta = {
        "allow_inheritance": False,
        "indexes": [
            {
                "fields": ("user", "assignment", "-most_recent", "-timestamp"),
                "types": False
            }
        ]
    }

    def getFilePath(self):
        return os.path.join(
            config["SUBMISSION_DIRECTORY"],
            str(self.assignment),
            self.user,
            str(self.id)
        )