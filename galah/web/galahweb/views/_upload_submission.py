## The Actual View ##
from galah.web.galahweb import app
from flask.ext.login import current_user
from galah.web.galahweb.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, request, flash, redirect, jsonify, \
                  url_for
from galah.db.models import Submission, Assignment
from galah.web.galahweb.util import is_url_on_site
import os.path
import subprocess
import datetime
import shutil
import tempfile

SUBMISSION_DIRECTORY = "/var/local/galah.web/submissions/"
assert SUBMISSION_DIRECTORY[0] == "/" # Directory must be given as absolute path

def prepare_new_submission(**kwargs):
    """
    Prepares a new submission object properly initialized with an id and a
    new testables directory to store the submission in.

    """
    
    # Create a new submission from the keyword arguments
    new_submission = Submission(**kwargs)
    
    # Create an id for the new submission if one doesn't yet exist
    new_submission.id = new_submission.id or ObjectId()
    
    if not new_submission.testables:
        # Craft a unique directory path where we will store the new submission
        new_submission.testables = os.path.join(
            SUBMISSION_DIRECTORY, str(new_submission.id)
        )
        
        # Create the directory. We are guarenteed an ObjectId is unique. However
        # we are not guarenteed that we will have the proper permissions and
        # that we will be able to make the directory thus this could error
        # because of that.
        os.makedirs(new_submission.testables)
        
    return new_submission
    
def abort_new_submission(submission):
    """
    Deletes and cleans up a submission THAT HAS NOT YET BEEN SAVED to Mongo by
    deleting the testables directory, etc.
    
    Call this if a created submission is found to be invalid during processing.
    
    """
    
    if submission.testables:
        # Delete the directory
        shutil.rmtree(submission.testables)

@app.route("/assignments/<assignment_id>/upload", methods = ["POST"])
@account_type_required("student")
def upload_submission(assignment_id):
    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        app.logger.debug("Invalid ID: Malformed.")
        
        abort(404)
    
    # Ensure that an assignment with the provided id actually exists
    if Assignment.objects(id = id).limit(1).count() == 0:
        app.logger.debug("Invalid ID: Assignment does not exist.")
        
        abort(404)
    
    def craft_response(**kwargs):
        if request.is_xhr:
            # If the request was made via ajax return a JSON object...
            return jsonify(**kwargs)
        else:
            # otherwise redirect to the correct view.
            if "error" in kwargs:
                flash(kwargs["error"], category = "error")
            elif "message" in kwargs:
                flash(kwags["message"], category = "message")
            else:
                flash("File(s) uploaded succesfully.", category = "message")
                
            redirect_to = request.args.get("next") or request.referrer
            
            if not is_url_on_site(app, redirect_to):
                # Default going back to the assignment screen
                redirect_to = url_for(
                    "view_assignment", 
                    assignment_id = assignment_id
                )
            
            return redirect(redirect_to)
    
    # Craft a new submission
    new_submission = prepare_new_submission(
        assignment = id,
        user = current_user.id,
        timestamp = datetime.datetime.now(),
        marked_for_grading = bool(request.form.get("marked_for_grading"))
    )
    
    # The user is uploading a single archive containing the entire submission
    if request.files.get("archive"):
        archive = request.files["archive"]
        
        # Create a temporary file that we will use to store the archive. It is
        # given to us open and as a tuple with some additional information so we
        # need to close it and extract only the information we need.
        temp_file = tempfile.mkstemp()
        os.close(temp_file[0])
        temp_file = temp_file[1]
        
        # Save the archive over the temp_file we just created
        archive.save(temp_file)
        
        # TODO: Find out if tar is secure! Can the archive be made such that
        # files will be placed outside of the directory were exporting the
        # tar into?? If so that's a huge security hole.
        try:
            if archive.filename.endswith(".tar"):
                subprocess.check_call(
                    ["tar", "xf", temp_file], 
                    cwd = new_submission.testables
                )
            elif archive.filename.endswith(".tar.gz"):
                subprocess.check_call(
                    ["tar", "xzf", temp_file], 
                    cwd = new_submission.testables
                )
            elif archive.filename.endswith(".zip"):
                subprocess.check_call(
                    ["unzip", temp_file],
                    cwd = new_submission.testables
                )
            else:
                abort_new_submission(new_submission)
                
                return craft_response(
                    error = "Uploaded file (%s) had an unrecognized extension."
                                % archive.filename
                )
        except subprocess.CalledProcessError:
            abort_new_submission(new_submission)
            
            return craft_response(
                error = "Uploaded file (%s) could not be opened as an archive."
                            % archive.filename
            )
        finally:
            # Always remove the temporary file we used to store the archive if
            # we succesfully created one
            if temp_file:
                os.remove(temp_file)
    else:
        # We did not recieve enough information to do anything
        return craft_response(error = "No files were selected for uploading.")
    
    # Determine what files actually got uploaded and save them into the
    # submission.
    for root, dirnames, filenames in os.walk(new_submission.testables):
        for filename in filenames:
            new_submission.uploaded_filenames.append(
                os.path.relpath(
                    os.path.join(root, filename), 
                    new_submission.testables
                )
            )
    
    # Persist! Otherwise nobody will know what happened this day.
    new_submission.save()
    
    # Communicate to the next page what submission was just added.
    flash(new_submission.id, category = "new_submission")
    
    # Everything seems to have gone well
    return craft_response(new_submission = new_submission)
