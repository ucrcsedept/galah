# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

class FlockMessage:
    __slots__ = ("type", "body")

    # Acceptable types for a shepherd/sheep to send or sheep/shepherd to
    # receive.
    shepherd_types = ("bloot", "identify", "request")
    sheep_types = ("bleet", "environment", "distress", "result")

    def __init__(self, type, body):
        self.type = type
        self.body = body

    def __str__(self):
        return "FlockMessage(type = \"%s\", body = \"%s\")" % (
            self.type, self.body
        )

    def to_dict(self):
        return {"type": self.type, "body": self.body}

    @staticmethod
    def from_dict(raw):
        return FlockMessage(raw["type"], raw["body"])

class TestRequest:
    """
    A basic test request as the shepherd would receive it from the outside.
    Contains only the submission id of the submission to test.

    """

    __slots__ = ("submission_id", )

    def __init__(self, submission_id):
        self.submission_id = submission_id

    def to_dict(self):
    	return {"submission_id": str(self.submission_id)}

    @staticmethod
    def from_dict(raw):
    	return TestRequest(raw["submission_id"])

class InternalTestRequest:
    """
    A more expressive test request as the shepherd would store it internally.
    The shepherd (or whoever) transforms a TestRequest object into an
    InternalTestRequest object upon receival.

    """

    __slots__ = ("submission_id", "timeout", "environment")

    def __init__(self, submission_id, timeout, environment):
        self.submission_id = submission_id
        self.timeout = timeout
        self.environment = environment

    def to_dict(self):
        return {
            "submission_id": self.submission_id,
            "timeout": self.timeout,
            "environment": self.environment
        }

    @staticmethod
    def from_dict(raw):
        return InternalTestRequest(
            raw["submission_id"],
            raw["timeout"],
            raw["environment"]
        )
