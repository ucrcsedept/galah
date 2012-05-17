from datetime import datetime

from mongoengine import *

from app.models.classes import Class
from app.models.users import User

from app.helpers.utils import Enum

class Invitation(Document):
    email = EmailField(required = True)
    class_ = ReferenceField(Class, CASCADE, required = True)
    expires = DateTimeField(required = True)
    accountType = IntField(choices = range(User.accountTypes.end()),
                           default = User.accountTypes.student)
    
    meta = {
        "allow_inheritance": False
    }
    
    def __init__(self, *zargs, **zkwargs):
        Document.__init__(self, *zargs, **zkwargs)
        
        if self.expires < datetime.today():
            raise ValueError("Invitation is expired")
