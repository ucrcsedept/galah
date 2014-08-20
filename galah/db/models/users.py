from mongoengine import *

# Load up the configuration for the email validation regular expression
from galah.base.config import load_config
config = load_config("global")

class User(Document):
    email = EmailField(unique = True, primary_key = True,
                       regex = config["EMAIL_VALIDATION_REGEX"])
    seal = StringField()
    account_type = StringField(choices = ["student", "teaching_assistant",
                                          "teacher", "admin"], required = True)
    classes = ListField(ObjectIdField())

    # The individual cutoff date
    personal_deadline = MapField(DateTimeField())

    # The individual due date
    personal_due_date = MapField(DateTimeField())

    meta = {
        "indexes": ["email", "classes"],
        "allow_inheritance": False
    }
