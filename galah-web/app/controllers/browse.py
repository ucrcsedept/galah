import web, datetime, pymongo, shutil, hashlib, os.path, config, json, \
       zmq, StringIO
from config import view
from bson.objectid import ObjectId

# Needed to diferentiate the Assignment class in this module with the model
import app.models as models

from app.models import *
from app.helpers import *

class SendSubmission:
    upload_map = {}
    
    def POST(self, zassignment):
        # TODO: This is full of hacky code but might be unavoidable thanks to
        # web.py. If/when migrating to Django clean this up.
        
        # Hack to ensure auth._session doesn't actually do anything (mainly were
        # worried about it creating an entirely new session because this page
        # may be requested without cookies).
        #auth._session._killed = True
        
        # Grab the POST data
        post = web.input(Filedata = "", session_id = None, done = None)
        
        # Ensure we we're given a session_id
        if not post.session_id:
            return "You are not logged in."
        
        # Grab the user's session from their session_id
        store = web.session.DiskStore("/var/local/galah-web/sessions")
        session_data = store[post.session_id]
        
        # Ensure a user is logged in
        if "user" not in session_data and session_data["user"]:
            return "You are not logged in."
            
        key = (session_data["user"], zassignment)
        
        if key not in SendSubmission.upload_map:
            newId = ObjectId()
            
            SendSubmission.upload_map[key] = {
                "submission": Submission(
                    id = newId,
                    assignment = ObjectId(zassignment),
                    user = session_data["user"],
                    timestamp = datetime.datetime.today(),
                    testables = "file://" + os.path.join("/var/local/galah-web/submissions/", str(newId))
                )
            }
            
            os.makedirs(os.path.join("/var/local/galah-web/submissions/", str(newId)))
        
        import sys
        print >> sys.stderr, post
        
        if post.done == "true":
            submissionDict = SendSubmission.upload_map[key]["submission"].to_mongo()
            
            # Save the submission to the database
            SendSubmission.upload_map[key]["submission"].save()
            
            # Send the submission to the shepherd
            shepherd = config.zmqContext.socket(zmq.DEALER)
            shepherd.connect("tcp://%s:%i" % (config.shepherdAddress, config.shepherdPort))
            shepherd.send(json.dumps(submissionDict, cls = mongoencoder.MongoEncoder))
        else:
            # TODO: Massive security vulnerability right here. Can you say "Welcome
            # to my server? Leave your coat anywere."
            file = open(os.path.join(SendSubmission.upload_map[key]["submission"].testables[7:], post.filename), "w")
            
            # Copy the contents of the uploaded file into the new one
            shutil.copyfileobj(StringIO.StringIO(post.Filedata), file)
        
        return "GOOD"

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
            
            # Save the submission to the database
            newSubmission.save()
            
            # Send the submission to the shepherd
            shepherd = config.zmqContext.socket(zmq.DEALER)
            shepherd.connect("tcp://%s:%i" % (config.shepherdAddress, config.shepherdPort))
            shepherd.send(json.dumps(submissionDict, cls = mongoencoder.MongoEncoder))

        return Assignment.GET(self, zassignment)
