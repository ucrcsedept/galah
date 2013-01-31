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

class SubTestResult(EmbeddedDocument):
    name = StringField()
    score = FloatField(required = True)
    max_score = FloatField(required = True)
    message = StringField()
    parts = ListField(ListField())

    def validate(self):
        for i in self.parts:
            if len(i) != 3:
                raise ValidationError("Every item in parts must have length 3.")

        return EmbeddedDocument.validate(self)

    meta = {
        "allow_inheritance": False
    }

    @staticmethod
    def from_dict(item):
        result = SubTestResult()

        # Go through every field the result has and extract that field from the
        # dict we were given.
        for i in result:
            if i in item:
                result.__setattr__(i, item.get(i))

        # Make sure all the correct fields were given and formatted correctly.
        result.validate()

        return result

class TestResult(Document):
    score = FloatField()
    max_score = FloatField()
    tests = ListField(EmbeddedDocumentField(SubTestResult))

    # Set to true if the test harness crashed or gave output rather than a valid
    # TestResult object.
    failed = BooleanField()

    meta = {
        "allow_inheritance": False
    }

    @staticmethod
    def from_dict(item):
        result = TestResult()

        # Go through every field the result has and extract that field from the
        # dict we were given.
        for i in result:
            if i == "id":
                pass

            elif i == "tests" and "tests" in item:
                for j in item.get(i):
                    result.tests.append(SubTestResult.from_dict(j))

            elif i in item:
                result.__setattr__(i, item.get(i))

        # Make sure all the correct fields were given and formatted correctly.
        result.validate()

        return result

import os.path

# Load up the configuration so we know where the submission directory is
from galah.base.config import load_config
config = load_config("global")

class Submission(Document):
    assignment = ObjectIdField(required = True)
    user = StringField(required = True)
    timestamp = DateTimeField(required = True)
    most_recent = BooleanField()
    test_type = StringField(choices = ["public", "final"])
    test_results = ObjectIdField()
    test_request_timestamp = DateTimeField()

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

    def to_dict(self):
        return {
            "id": str(self.id),
            "assignment": str(self.assignment),
            "user": self.user,
            "timestamp": self.timestamp.isoformat(),
            "most_recent": self.most_recent,
            "test_type": self.test_type,
            "test_results": self.test_results,
            "test_request_timestamp":
                    None if not self.test_request_timestamp else
                        self.test_request_timestamp.isoformat()
        }

    def getFilePath(self):
        return os.path.join(
            config["SUBMISSION_DIRECTORY"],
            str(self.assignment),
            self.user,
            str(self.id)
        )
