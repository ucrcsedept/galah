import json, iso8601, datetime
from bson.objectid import ObjectId

class MongoEncoder(json.JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return {"_type": "ObjectId", "value": str(obj)}
        elif isinstance(obj, datetime.datetime):
            return {"_type": "datetime", "value": obj.isoformat()}
        else:
            return json.JSONEncoder.default(self, obj, **kwargs)

