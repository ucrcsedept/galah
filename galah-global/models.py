"""
This module defines rigorously the objects that may pass from components of
Galah to other components and provides tools to convert them to and from
dictionaries with verification.

"""

from pymongo.objectid import ObjectId
from datetime import datetime

class SimpleStruct:
    schema = { }
    metaOptions = { }
    def __init__(self, **zentries):
        self.__dict__.update(zentries)
        
    def _validate(self, zschema, zmetaOptions):
        # Iterate through every member in this SimpleStruct
        for i, j in self.__dict__.items():
            # Ensure that the current member is in the schema
            if i not in zschema:
                if zmetaOptions.get("exclusive"):
                    return false
                else:
                    continue
            
            if 
            if type(j) is not zschema[i]:
                return False
        
class TestResult(SimpleStruct):
    metaOptions = {"exclusive": True}
    schema = {
        "username": unicode,
        "assignment": ObjectId,
        "timestamp": datetime,
        "messages": [{"type": list, "contains": unicode}, unicode}],
        "name": unicode,
        "score": {"type": float, "optional": True},
        "maxScore": {"type": float, "optional": True},
        "results": {"type": list, "contains": SubTestResult}
    }
