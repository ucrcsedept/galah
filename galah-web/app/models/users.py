import app.helpers.pbkdf2, app.helpers.utils, os, copy

from mongoengine import *
from app.helpers import *

from app.models.classes import Class

class User(Document):
    accountTypes = utils.Enum("student instructor admin")
    
    email = EmailField(unique = True, primary_key = True)
    hash = StringField(required = True)
    accountType = IntField(choices = range(accountTypes.end()), required = True)
    classes = ListField(ObjectIdField())
    teaching = ListField(ObjectIdField())
    
    meta = {
        "indexes": ["email", "classes", "teaching"],
        "allow_inheritance": False
    }
    
    def checkPassword(self, zpassword):
        "Returns true iff *zpassword* is the correct password for this user."
        
        hashInfo = utils.HashInfo.fromString(self.hash)

        return utils.safeStrCmp(hashInfo.hashString(zpassword), hashInfo.hash)
        
    @staticmethod
    def createHash(zpassword):
        """
        Convenience function that uses *HashInfo* to create a hash *zpassword*.
        
        **Note:** This function will return a stringified *HashInfo*, not just
        the hash part of it.
        
        """
        
        hashInfo = utils.HashInfo("PBKDF2-256", os.urandom(4).encode("hex"), 1000)
        hashInfo.hash = hashInfo.hashString(zpassword)
        
        return str(hashInfo)        
