import config, app.helpers.pbkdf2, app.helpers.utils, os, copy
from app import helpers

from mongoengine import *

from app.models.classes import Class

class User(Document):
    accountTypes = helpers.utils.Enum("student instructor admin")
    
    email = EmailField(unique = True, primary_key = True)
    hash = StringField(required = True)
    accountType = IntField(choices = range(accountTypes.end()), required = True)
    classes = ListField(ReferenceField(Class, NULLIFY))
    
    meta = {
        "indexes": ["email", "classes"],
        "allow_inheritance": False
    }
    
    def checkPassword(self, zpassword):
        "Returns true iff *zpassword* is the correct password for this user."
        
        hashInfo = HashInfo.fromString(self.hash)

        return helpers.utils.safeStrCmp(hashInfo.hashString(zpassword),
                                        hashInfo.hash)
        
    @staticmethod
    def createHash(zpassword):
        """
        Convenience function that uses *HashInfo* to create a hash *zpassword*.
        
        **Note:** This function will return a stringified *HashInfo*, not just
        the hash part of it.
        
        """
        
        hashInfo = HashInfo("PBKDF2-256", os.urandom(4).encode("hex"), 1000)
        hashInfo.hash = hashInfo.hashString(zpassword)
        
        return str(hashInfo)        

class HashInfo:
    "Utility class for dealing with hashed passwords in the database."
    
    def __init__(self, zalgorithm = "", zsalt = "", zcostFactor = 0, zhash = ""):
        self.algorithm = str(zalgorithm)
        self.salt = str(zsalt)
        self.costFactor = int(zcostFactor)
        self.hash = str(zhash)
    
    def hashString(self, zstr):
        """
        Hashes a string given the algorithm, salt, and costFactor for this
        object.
        
        """
        
        assert self.algorithm == "PBKDF2-256"
        
        return helpers.pbkdf2.pbkdf2_hex(str(zstr), str(self.salt), self.costFactor)
    
    @classmethod
    def fromString(cls, zstring):
        "Deconstructs a string into a PassInfo object"
        
        # Create a new instance
        obj = cls()
        
        # Deconstruct the string
        passInfo = zstring.split(":")

        # Fill in the datamembers
        obj.algorithm = str(passInfo[0])
        obj.salt = str(passInfo[1])
        obj.costFactor = int(passInfo[2])
        obj.hash = str(passInfo[3])
        
        return obj
    
    def __str__(self):
        return ":".join((self.algorithm, self.salt, str(self.costFactor), self.hash))
