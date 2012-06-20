from datetime import datetime

from mongoengine import *

class Invitation(Document):
    email = EmailField(required = True)
    class_ = ObjectIdField(required = True)
    expires = DateTimeField(required = True)
    accountType = StringField(required = True)
    
    meta = {
        "allow_inheritance": False
    }
    
    def __init__(self, *zargs, **zkwargs):
        Document.__init__(self, *zargs, **zkwargs)
        
        if self.expires < datetime.today():
            raise ValueError("Invitation is expired")
