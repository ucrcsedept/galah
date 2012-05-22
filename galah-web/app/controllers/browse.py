import web, datetime, pymongo
from config import view
from app.helpers import utils
from app.helpers.exceptions import UserError

import app.helpers.auth as auth

import app.models as models

from pymongo.objectid import ObjectId

class Assignments:
    @auth.authenticationRequired
    def GET(self):
        user = models.User.objects.get(email = auth.authenticated())

        # Get a list of all the classes the user belongs to.
        classes = models.Class.objects(id__in = user.classes)
        
        # Get all of the assignments in those classes
        assignments = models.Assignment.objects(forClass__in = user.classes)
        
        # Add the className attribute to all the assignments so the view can
        # access it easily.
        for i in assignments:
            try:
                i["className"] = \
                    utils.first(classes, lambda j: j.id == i["forClass"]).name
            except:
                i["className"] = "NONE"
        
        return view.assignments(assignments, classes)

class Assignment:
    @auth.authenticationRequired
    def GET(self, zassignment):
        user = models.User.objects.get(email = models.authentication.authenticated())
        
        # Convert the assignment in the URL into an ObjectId
        id = ObjectId(zassignment)
        
        # Retrieve the assignment
        assignment = models.assignments.fromId(id)
        
        if assignment == None:
            raise UserError("Assignment was not found.")
        
        # Retrieve the name of the class the assignment belongs to
        class_ = Class.objects.get(id = assignment["class"])
        
        # Ensure that a class was found
        if class_ == None:
            raise UserError("You are not in the correct class.")
        
        assert assignment != None, "Exists in a class page but doesn't exist " \
                                   "assignments collection."
        
        # Add class information so the template can access it easily
        assignment["className"] = class_.name
        
        # Get all of the test results for this assignmnet
        testResults = models.testresults.fromUserAssignment("john", id)
        
        return view.assignment(assignment, class_, testResults)
