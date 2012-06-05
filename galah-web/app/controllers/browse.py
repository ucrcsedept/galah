import web, datetime, pymongo, shutil, hashlib, os.path
from config import view
from pymongo.objectid import ObjectId

# Needed to diferentiate the Assignment class in this module with the model
import app.models as models

from app.models import *
from app.helpers import *

from pymongo.objectid import ObjectId

class Assignments:
    @auth.authenticationRequired
    def GET(self):
        user = User.objects.get(email = auth.authenticated())
        
        classes = Class.objects(id__in = user.classes).only("name")
        
        # Get all of the assignments in those classes
        assignments = list(models.Assignment.objects(forClass__in = user.classes))
        
        # Add the className attribute to all the assignments so the view can
        # access it easily.
        for i in assignments:
            assert "className" not in vars(i)
            
            i.className = \
                utils.first(classes, lambda j: j.id == i.forClass).name
        
        return view.assignments(assignments, classes)

class Assignment:
    @auth.authenticationRequired
    def GET(self, zassignment):
        user = User.objects.get(email = auth.authenticated())
        
        # Convert the assignment in the URL into an ObjectId
        id = ObjectId(zassignment)
        
        # Retrieve the assignment
        assignment = models.Assignment.objects.get(id = id)
        
        if assignment == None:
            raise UserError("Assignment was not found.")
        
        # Retrieve the name of the class the assignment belongs to
        className = Class.objects(id = assignment.forClass).only("name").first()
        
        assert className != None, "Assignment pointing to non-existant class."
        
        # Add class information so the template can access it easily
        assignment.className = className
        
        # Get all of the test results for this assignmnet
        testResults = list(TestResult.objects(user = user.id, assignment = id))
        
        return view.assignment(assignment, testResults)
 
    @auth.authenticationRequired
    def POST(self, zassignment):
        user = User.objects.get(email = auth.authenticated())
        
        # Convert the assignment in the URL into an ObjectId
        id = ObjectId(zassignment)
        
        # Retrieve the assignment
        assignment = models.Assignment.objects.get(id = id)
        
        post = web.input(new_submission = {})
        
        save_to = "/tmp/galah/"
        
        if "new_submission" in post:
            # Come up with a name for the file and open it
            fileId = ObjectId()
            file = open(os.path.join(save_to, str(fileId)), "wb")
            
            # Copy the contents of the uploaded file into the new one
            shutil.copyfileobj(post.new_submission.file, file)
            
            # Craft a new test request
            testRequest = {
                "assignment": str(id),
                "testDriver": 
            }

        return Assignment.GET(self, zassignment)
