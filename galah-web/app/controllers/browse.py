import web, datetime, pymongo, shutil, hashlib, os.path, config
from config import view
from bson.objectid import ObjectId

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
        
        return view.assignment(assignment, testResults, user.repos.get(str(id)))
 
    @auth.authenticationRequired
    def POST(self, zassignment):
        user = User.objects.get(email = auth.authenticated())
        
        # Convert the assignment in the URL into an ObjectId
        id = ObjectId(zassignment)
        
        # Retrieve the assignment
        assignment = models.Assignment.objects.get(id = id)
        
        post = web.input(new_submission = {})
        
        save_to = "/tmp/galah/"
        
        if "git_repo" in post and post.git_repo:
            user.repos[str(id)] = post.git_repo
            user.save()
        elif "new_submission" in post:
            import subprocess, tempfile, os, zmq
            
            # The repo the file will be uploaded to
            repo = user.repos[str(id)]
            
            # Come up with a name for the file and open it
            file = tempfile.NamedTemporaryFile(mode = "wb", delete = False)
            
            # Copy the contents of the uploaded file into the new one
            shutil.copyfileobj(post.new_submission.file, file)
            
            # Close the file
            file.close()
            
            # Get a temporary directory for us to play in
            directory = tempfile.mkdtemp()
            
            # Untar the archive into the directory
            if subprocess.call(["tar", "-xf", file.name], cwd = directory) != 0:
                raise RuntimeError("Not a valid tar file.")
                
            # Remove the tar file now that we've extracted its contents
            os.remove(file.name)
            
            # Update the git repo with the files inside the tar file
            a = subprocess.call([config.pullScript, repo], cwd = directory)
            assert a == 0
            
            # Craft a new test request
            testRequest = {
                "assignment": str(id),
                "testDriver": "cat",
                "testables": repo,
                "user": user.email,
                "actions": ["test.c"]
            }
            
            shepherd = config.zmqContext.Socket(zmq.DEALER)
            shepherd.connect("tcp://%s:%i" % (config.shepherdAddress, config.shepherdPort))
            shepherd.send_json(testRequest)
        else:
            assert False

        return Assignment.GET(self, zassignment)
