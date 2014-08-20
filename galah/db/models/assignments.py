from mongoengine import *
import datetime

class TestHarness(Document):
    # The harness's user-defined configuration. May contain any key value pairs,
    # but certain pairs have special meaning:
    #    * "galah/TIMEOUT" is the number of seconds to allow the test harness to
    #      run before the entire VM is brutally destroyed.
    #    * "galah/ENVIRONMENT" is a dictionary that explains the environment
    #      that the VM must have.
    config = DictField()

    # The directory on the filesystem that has the test harness stored within it.
    harness_path = StringField(required = True)

    meta = {
        "allow_inheritance": False
    }

    def to_dict(self):
        return {
            "config": self.config,
            "harness_path": self.harness_path,
            "id": str(self.id)
        }

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    due_cutoff = DateTimeField()
    hide_until = DateTimeField(default = datetime.datetime.min, required = True)
    for_class = ObjectIdField(required = True)
    test_harness = ObjectIdField()
    allow_final_submission = BooleanField(default = True)

    meta = {
        "allow_inheritance": False
    }

    def to_dict(self):
        return {
            "name": self.name,
            "due": self.due.isoformat(),
            "due_cutoff":
                None if not self.due_cutoff else self.due_cutoff.isoformat(),
            "hide_until": str(self.for_class),
            "test_harness": str(self.test_harness)
        }

    def validate(self, clean = True):
        if self.due_cutoff and self.due > self.due_cutoff:
            raise ValidationError("due cannot be later than due_cutoff")

        return Document.validate(self)

    def apply_personal_deadlines(self, user):
        self.due_cutoff = user.personal_deadline.get(
            str(self.id), self.due_cutoff
        )

        self.due = user.personal_due_date.get(
            str(self.id), self.due
        )
