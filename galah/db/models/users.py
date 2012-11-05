from mongoengine import *

class User(Document):
    email = EmailField(unique = True, primary_key = True)
    seal = StringField()
    account_type = StringField(choices = ["student", "teacher", "admin"], required = True)
    classes = ListField(ObjectIdField())
    
    meta = {
        "indexes": ["email", "classes"],
        "allow_inheritance": False
    }
