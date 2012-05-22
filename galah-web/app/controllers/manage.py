import web, datetime, pymongo
from config import view
from app.helpers import utils
from app.helpers.exceptions import UserError

import app.helpers.auth as auth

import app.models as models

from pymongo.objectid import ObjectId

class Classes:
    @auth.authenticationRequired
    def GET(self):
        user = models.User.objects.get(email = auth.authenticated())

        # Get a list of all the classes the user is teaching.
        classes = list(user.classes)
        
        # Get all of the assignments in those classes
        assignments = models.Assignment.objects(forClass__in = user.classes)
        
        # Add the className attribute to all the assignments so the view can
        # access it easily.
        for i in assignments:
            # Ensure that we aren't about to blow away something we shouldn't
            assert "className" not in vars(i)
            
            vars(i)["className"] = \
                utils.first(classes, lambda j: j.id == i.forClass).name
        
        return view.classes(assignments, classes)
