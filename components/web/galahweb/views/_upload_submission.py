## The Actual View ##
from galahweb import app
from flask.ext.login import current_user
from galahweb.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, request
from galah.db.models import Submission, Assignment
import os.path
import subprocess
import datetime
import shutil
import tempfile

SUBMISSION_DIRECTORY = "/var/local/galah.web/submissions/"

@app.route("/assignments/<assignment_id>/upload", methods = ["POST"])
@account_type_required("student")
def upload_submission(assignment_id):
    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        app.logger.debug("Invalid ID")
        
        abort(404)
    
    # Ensure that an assignment with the provided id actually exists
    if Assignment.objects(id = id).limit(1).count() == 0:
        abort(404)
    
    # Craft a new submission
    new_submission = Submission(
        id = ObjectId(),
        assignment = id,
        user = current_user.id,
        timestamp = datetime.datetime.now()
    )
    
    # The user is uploading a single archive containing the entire submission
    if request.files.get("archive"):
        archive = request.files["archive"]
        
        # Store the archive somewhere on the filesystem so we can access it
        temp_file = tempfile.mkstemp()
        
        # We don't want an open file handle to the temporary file so close it
        os.close(temp_file[0])
        
        # All we're interseted in is that path to the file
        temp_file = temp_file[1]
        
        # Save the archive over the temp_file we just created
        archive.save(temp_file)
        
        # Figure out where we will store this submission
        directory = os.path.join(SUBMISSION_DIRECTORY, str(new_submission.id))
        
        new_submission.testables = directory
        
        # Create the directories needed (this will try to create the entire
        # directory tree if necessary).
        os.makedirs(directory)
        
        # TODO: Find out if tar is secure! Can the archive be made such that
        # files will be placed outside of the directory were exporting the
        # tar into?? If so that's a huge security hole.
        # TODO: It would be nice if zip was supported. The reason it's not
        # for now is that the unzip program won't accept an archie from
        # standard input.
        try:
            if archive.filename.endswith(".tar"):
                subprocess.check_call(
                    ["tar", "xf", temp_file], 
                    cwd = directory
                )
            elif archive.filename.endswith(".tar.gz"):
                subprocess.check_call(
                    ["tar", "xzf", temp_file], 
                    cwd = directory
                )
            else:
                return "Invalid Filetype"
        except subprocess.CalledProcessError:
            # Delete the directory
            shutil.rmtree(directory)
            
            return "Invalid Filetype"
        finally:
            os.remove(temp_file)
    else:
        return "NTD"
    
    return "GOOD"
