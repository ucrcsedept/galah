import web, datetime, pymongo, shutil, hashlib, os.path, config, json
from config import view
from bson.objectid import ObjectId

# Needed to diferentiate the Assignment class in this module with the model
import app.models as models

from app.models import *
from app.helpers import *

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
    storage = submit.FileStore()
    
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
        
        # Get all of the submissions for this assignmnet
        submissions = list(Submission.objects(user = user.id, assignment = id))
        
        return view.assignment(assignment, submissions)
 
    @auth.authenticationRequired
    def POST(self, zassignment):
        user = User.objects.get(email = auth.authenticated())
        
        # Convert the assignment in the URL into an ObjectId
        id = ObjectId(zassignment)
        
        # Retrieve the assignment
        assignment = models.Assignment.objects.get(id = id)
        
        if assignment == None:
            raise UserError("Assignment was not found.")
        
        post = web.input(new_submission = {})
        
        save_to = "/tmp/galah/"
        
        if "new_submission" in post:
            import subprocess, tempfile, os, zmq
            
            # Determine the file's type
            suffix = post.new_submission.filename
            if suffix.endswith(".tar.gz"):
                suffix = ".tar.gz"
            elif suffix.endswith(".zip"):
                suffix = ".zip"
            else:
                raise UserError("Only .tar.gz and .zip files are allowed")
            
            # Get a temporary file that we can store the uploaded file in
            file = tempfile.NamedTemporaryFile(
                mode = "wb", delete = False, suffix = suffix
            )
            
            # Copy the contents of the uploaded file into the new one
            shutil.copyfileobj(post.new_submission.file, file)
            
            # Close the file
            file.close()
            
            # Craft a new submission object
            newSubmission = Submission(
                assignment = id,
                user = user.id,
                timestamp = datetime.datetime.today()
            )
            
            # Store the submission
            newSubmission.testables = \
                self.storage.store(newSubmission, file.name)
            
            submissionDict = newSubmission.to_mongo()
            
            # Send the submission to the shepherd
            shepherd = config.zmqContext.socket(zmq.DEALER)
            shepherd.connect("tcp://%s:%i" % (config.shepherdAddress, config.shepherdPort))
            shepherd.send(json.dumps(submissionDict, cls = mongoencoder.MongoEncoder))

        return Assignment.GET(self, zassignment)
