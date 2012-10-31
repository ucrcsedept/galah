from inspect import getargspec
from warnings import warn
from copy import deepcopy
from bson import ObjectId
from bson.errors import InvalidId
from galah.db.models import *
import json
from collections import namedtuple
from mongoengine import ValidationError

#: An anonymous admin user useful when accessing this module from the local
#: system.
admin_user = namedtuple("User", "account_type")("admin")
           
class APICall(object):
    """Wraps an API call and handles basic permissions along with providing a
    simple interface to get meta data on the API call.
    
    """
    
    __slots__ = ("wrapped_function", "allowed", "argspec", "name")
            
    class PermissionError(RuntimeError):
        def __init__(self, *args, **kwargs):
            RuntimeError.__init__(self, *args, **kwargs)
    
    def __init__(self, wrapped_function, allowed = None):
        #: The raw function we are wrapping that performs the actual logic.
        self.wrapped_function = wrapped_function
        
        #: The account types that are allowed to call this function, if None 
        #: any account type may call this function.
        self.allowed = allowed
        
        #: Information about the arguments this API call accepts in the same
        #: format :func: inspect.getargspec returns.
        self.argspec = getargspec(wrapped_function)
        
        #: The name of the wrapped function.
        self.name = wrapped_function.func_name
        
    def __call__(self, current_user, *args, **kwargs):
        arg_spec = getargspec(self.wrapped_function)
        
        # If no validation is required this won't actually be a problem, however
        # it's certainly not something that you should be doing.
        if not hasattr(current_user, "account_type"):
            # !! Purposely exceeds 80 character cap for formatting reason. Do
            #    not "fix."
            warn("current_user (%s) is not a valid user object." % repr(current_user))
        
        # Check if the current user has permisson to perform this operation
        if self.allowed and current_user.account_type not in self.allowed:
            raise APICall.PermissionError(
                "Only %s users are allowed to call %s" %
                    (
                        " or ".join(self.allowed),
                        self.wrapped_function.func_name
                    )
            )
        
        # Only pass the current user to the function if the function wants it
        if len(self.argspec[0]) != 0 and self.argspec[0][0] == "current_user":
            return str(self.wrapped_function(current_user, *args, **kwargs))
        else: 
            return str(self.wrapped_function(*args, **kwargs))

from decorator import decorator

def _api_call(allowed = None):
    """Decorator that wraps a function with the :class: APICall class."""
    
    if isinstance(allowed, basestring):
        allowed = (allowed, )

    def inner(func):
        return APICall(func, allowed)

    return inner

## Some useful low level functions ##
def _get_user(email, current_user):
    if email == "me":
        return current_user

    try:
        return User.objects.get(email = email)
    except User.DoesNotExist:
        raise RuntimeError("User %s does not exist." % email)

def _user_to_str(user):
    return "User [email = %s, account_type = %s]" % \
            (user.email, user.account_type)

def _get_assignment(id):
    try:
        return Assignment.objects.get(id = ObjectId(id))
    except Assignment.DoesNotExist:
        raise RuntimeError("Assignment with ID %s does not exist." % id)
    except InvalidId:
        raise RuntimeError("Assignment ID %s is not a valid ID." % id)

def _assignment_to_str(assignment):
    return "Assignment [id = %s, name = %s]" % (assignment.id, assignment.name)

def _get_class(query, instructor = None):
    try:
        query_dict = {"id": ObjectId(query)}
        if instructor:
            query_dict["id__in"] = instructor.classes

        # Check if the user provided a valid ObjectId
        return Class.objects.get(**query_dict)
    except (Class.DoesNotExist, InvalidId):
        pass

    query_dict = {"name__icontains": query}
    if instructor:
        query_dict["id__in": instructor.classes]

    matches = list(Class.objects(**query_dict))
    
    if not matches:
        raise RuntimeError("No classes matched your query of '%s'." % query)    
    elif len(matches) == 1:
        return matches[0]
    else:
        raise RuntimeError(
            "%d classes match your query of '%s', however, this API expects 1 "
            "class. Refine your query and try again.\n\t%s" % (
                len(matches),
                query, 
                "\n\t".join(_class_to_str(i) for i in matches)
            )
        )

def _class_to_str(the_class):
    return "Class [id = %s, name = %s]" % (the_class.id, the_class.name)
        
import datetime
def _to_datetime(time):
    try:
        return datetime.datetime(time)
    except TypeError:
        pass
        
    try:
        return datetime.datetime.strptime(time, "%m/%d/%Y %H:%M:%S")
    except (OverflowError, ValueError):
        raise ValueError(
            "Could not convert %s into a time object." % repr(time)
        )
        
## Below are the actual API calls ##
@_api_call()
def get_api_info():
    # This function should be memoized
    
    api_info = []
    for k, v in api_calls.items():
        api_info.append({"name": k})
        current = api_info[-1]
        
        # Loop through all the arguments the function takes in and add
        # information on each argument to the api_info
        current["args"] = []
        for i in xrange(len(v.argspec.args)):
            current["args"].append({"name": v.argspec.args[i]})
            
            if v.argspec.defaults:
                # The number of arguments without default values
                ndefaultless = len(v.argspec.args) - len(v.argspec.defaults)
                
                # If the current argument has a default value make note of it
                if ndefaultless <= i:
                    current["args"][-1].update({
                        "default_value": v.argspec.defaults[i - ndefaultless]
                    })
    
    return json.dumps(api_info, separators = (",", ":"))

from galah.db.crypto.passcrypt import serialize_seal, seal
from mongoengine import OperationError
@_api_call("admin")
def create_user(email, password, account_type = "student"):
    new_user = User(
        email = email, 
        seal = serialize_seal(seal(password)), 
        account_type = account_type
    )
    
    try:
        new_user.save(force_insert = True)
    except OperationError:
        raise RuntimeError("A user with that email already exists.")
    
    return "Success! %s created." % _user_to_str(new_user)

@_api_call("admin")
def reset_password(current_user, email, new_password):
    the_user = _get_user(email, current_user)

    the_user.seal = serialize_seal(seal(new_password))

    the_user.save()

    return "Success! Password for %s succesfully reset." \
                % _user_to_str(the_user)

@_api_call("admin")
def modify_user(current_user, email, account_type):
    the_user = _get_user(email, current_user)

    old_user_string = _user_to_str(the_user)

    the_user.account_type = account_type

    try:
        the_user.save()
    except ValidationError:
        raise RuntimeError("%s is not a valid account type." % account_type)

    return "Success! %s has been retyped as a %s" \
                % (old_user_string, account_type)

@_api_call(("admin", "teacher"))
def find_user(current_user, email_contains = "", account_type = "",
              enrolled_in = ""):
    query = {}
    query_description = []

    if email_contains:
        query["email__icontains"] = email_contains
        query_description.append("email contains '%s'" % email_contains)

    if account_type:
        query["account_type"] = account_type
        query_description.append("account type is '%s'" % account_type)

    if enrolled_in:
        the_class = _get_class(enrolled_in)
        query["classes"] = the_class.id
        query_description.append("enrolled in %s" %
                _class_to_str(the_class))

    matches = list(User.objects(**query))

    if query_description:
        query_description = ",".join(query_description)
    else:
        query_description = "any"

    result_string = "\n\t".join(_user_to_str(i) for i in matches)

    return "%d user(s) found matching query {%s}.\n\t%s" % \
            (len(matches), query_description, result_string)

@_api_call(("admin", "teacher"))
def user_info(current_user, email):
    user = _get_user(email, current_user)

    enrolled_in = Class.objects(id__in = user.classes)

    class_list = "\n\t".join(_class_to_str(i) for i in enrolled_in)

    if not enrolled_in:
        return "%s is not enrolled in any classes." % _user_to_str(user)
    else:
        return "%s is enrolled in:\n\t%s" % (_user_to_str(user), class_list)

@_api_call("admin")
def delete_user(current_user, email):    
    to_delete = _get_user(email, current_user)

    to_delete.delete()
        
    return "Success! %s deleted." % _user_to_str(to_delete)
    
@_api_call(("admin", "teacher"))
def find_class(current_user, name_contains = "", enrollee = ""):
    if not enrollee and current_user.account_type != "admin":
        query = {"id__in": current_user.classes}
        instructor_string = "You are"
    elif enrollee == "any" or current_user.account_type == "admin":
        query = {}
        instructor_string = "Anyone is"
    else:
        the_instructor = _get_user(enrollee, current_user)
        query = {"id__in": the_instructor.classes}
        instructor_string = _user_to_str(the_instructor) + " is"
        
    if name_contains:
        query["name__icontains"] = name_contains

    matches = list(Class.objects(**query))

    result_string = "\n\t".join(_class_to_str(i) for i in matches)

    return "%s teaching %d class(es) with '%s' in their name.\n\t%s" % \
            (instructor_string, len(matches), name_contains, result_string)

@_api_call(("admin", "teacher"))
def enroll_student(current_user, email, enroll_in):
    user = _get_user(email, current_user)

    if current_user.account_type != "admin" and \
            user.account_type == "teacher":
        raise RuntimeError("Only admins can assign teachers to classes.")
    
    the_class = _get_class(enroll_in)

    if the_class.id in user.classes:
        raise RuntimeError("%s is already enrolled in %s." %
            (_user_to_str(user), _class_to_str(the_class))
        )
            
    user.classes.append(the_class.id)
    user.save()
    
    return "Success! %s enrolled in %s." % (
        _user_to_str(user), _class_to_str(the_class)
    )

@_api_call("admin")
def assign_teacher(current_user, email, assign_to):
    return enroll_student(current_user, email, assign_to)

@_api_call(("admin", "teacher"))
def drop_student(current_user, email, drop_from):    
    if current_user.account_type == "admin":
        the_class = _get_class(drop_from)
    else:
        the_class = _get_class(drop_from, current_user)

    user = _get_user(email, current_user)
        
    if the_class.id not in user.classes:
        raise RuntimeError("%s is not enrolled in %s." %
            (_user_to_str(user), _class_to_str(the_class))
        )
    
    user.classes.remove(the_class.id)
    user.save()
    
    return "Success! Dropped %s from %s." % (
        _user_to_str(user), _class_to_str(the_class)
    )

@_api_call(("admin", "teacher"))
def unassign_teacher(current_user, email, drop_from):
    return drop_student(current_user, email, drop_from)

@_api_call(("admin", "teacher"))
def class_info(for_class):
    the_class = _get_class(for_class)

    assignments = Assignment.objects(for_class = the_class.id)
    if assignments:
        assignments_string = "\n\t".join(
            _assignment_to_str(i) for i in assignments
        )
    else:
        assignments_string = "(No assignments)"

    return _class_to_str(the_class) + " has assignments:\n\t" + \
            assignments_string

@_api_call("admin")
def create_class(name):
    new_class = Class(name = name)
    new_class.save()
    
    return "Success! %s created." % _class_to_str(new_class)

@_api_call("admin")
def modify_class(the_class, name):
    if not name:
        raise RuntimeError("name cannot be empty.")

    the_class = _get_class(the_class)

    old_class_string = _class_to_str(the_class)

    the_class.name = name

    the_class.save()

    return "Success! %s has been renamed to '%s'" % (old_class_string, name)

@_api_call("admin")
def delete_class(to_delete):
    the_class = _get_class(to_delete)
        
    # Get all of the assignments for the class
    assignments = list(Assignment.objects(for_class = the_class.id))

    if assignments:
        assignments_string = \
            "\n\t".join(_assignment_to_str(i) for i in assignments)
    else:
        assignments_string = "(No assignments found)"

    # Then delete them
    Assignment.objects(for_class = the_class.id).delete()

    # Then un-enroll all users who are enrolled in the class (note this is
    # pretty expensive).
    for i in User.objects(classes = the_class.id):
        i.classes.remove(the_class.id)
        i.save()
        
    the_class.delete()
    
    return ("Success! %s deleted, and all of its assignments:\n\t%s"
                % (_class_to_str(the_class), assignments_string))

@_api_call(("admin", "teacher"))
def create_assignment(current_user, name, due, for_class, due_cutoff = ""):
    # The attributes of the assignmnet we're creating
    atts = {"name": name}

    atts["due"] = _to_datetime(due)

    if due_cutoff:
        atts["due_cutoff"] = _to_datetime(due_cutoff)

    the_class = _get_class(for_class)

    if current_user.account_type != "admin" and \
            the_class.id not in current_user.classes:
        raise RuntimeError(
            "You cannot create an assignment for a class you are not teaching."
        )

    atts["for_class"] = the_class.id

    print atts
    new_assignment = Assignment(**atts)
    new_assignment.save()
    
    return "Success! %s created." % _assignment_to_str(new_assignment)

@_api_call(("admin", "teacher"))
def assignment_info(id):
    assignment = _get_assignment(id)

    attribute_strings = []
    for k, v in assignment._data.items():
        if k and v:
            attribute_strings.append("%s = %s" % (k, v))

    attributes = "\n\t".join(attribute_strings)

    return "Properties of %s:\n\t%s" \
                % (_assignment_to_str(assignment), attributes)

@_api_call(("admin", "teacher"))
def modify_assignment(current_user, id, name = "", due = "", for_class = "",
                      due_cutoff = ""):
    assignment = _get_assignment(id)

    # Save the string representation of the original assignment show we can show
    # it to the user later.
    old_assignment_string = _assignment_to_str(assignment)

    if current_user.account_type != "admin" and \
            assignment.for_class not in current_user.classes:
        raise RuntimeError(
            "You can only modify assignments for classes you teach."
        )

    change_log = []

    if name:
        change_log.append(
            "Name changed from '%s' to '%s'." % (assignment.name, name)
        )

        assignment.name = name

    if due:
        due_date = _to_datetime(due)

        change_log.append(
            "Due date changed from '%s' to '%s'."
                % (str(assignment.due), str(due_date))
        )

        assignment.due = due_date

    if due_cutoff:
        cutoff_date = _to_datetime(due)

        change_log.append(
            "Cutoff date changed from '%s' to '%s'."
                % (str(assignment.due_cutoff), str(cutoff_date))
        )

        assignment.due_cutoff = cutoff_date

    if for_class:
        old_class = Class.objects.get(id = ObjectId(assignment.for_class))
        new_class = _get_class(for_class)

        change_log.append(
            "Class changed from %s to %s."
                % (_class_to_str(old_class), _class_to_str(new_class))
        )

        assignment.for_class = new_class.id

        if current_user.account_type != "admin" and \
                assignment.for_class not in current_user.classes:
            raise RuntimeError(
                "You cannot reassign an assignment to a class you're not "
                "teaching."
            )

    assignment.save()

    if change_log:
        change_log_string = "\n\t".join(change_log)
    else:
        change_log_string = "(No changes)"

    return "Success! The following changes were applied to %s.\n\t%s" \
                % (old_assignment_string, change_log_string)

@_api_call(("admin", "teacher"))
def delete_assignment(current_user, id):
    """Deletes an assignment.

    :param id: The ID of the assignment to delete.

    :returns: None

    :raises RuntimeError: If the assignment could not be deleted.

    """

    to_delete = _get_assignment(id)

    if current_user.account_type != "admin" and \
            to_delete.for_class not in current_user.classes:
        raise RuntimeError(
            "You cannot delete an assignment for a class you're not teaching."
        )

    to_delete.delete()
    
    return "Success! %s deleted." % _assignment_to_str(to_delete)

import threading
import Queue
tar_tasks_queue = Queue.Queue()
tar_tasks_thread = None

# Copied from web.views._upload_submission.SUBMISSION_DIRECTORY. Adding a new
# submission should be transformed into an API call and _upload_submissions
# should use that API call, but this will work for now.
SUBMISSION_DIRECTORY = "/var/local/galah.web/submissions/"

import tempfile
import os
import subprocess
def tar_tasks():
    # The thread that executes this function should execute as a daemon,
    # therefore there is no reason to allow an explicit exit. It will be 
    # brutally killed once the app exits.
    while True:
        # Block until we get a new task.
        task = tar_tasks_queue.get()

        # Find any expired archives and remove them
        # TODO: Remove the actual archives as well.
        Archive.objects(expires__lt = datetime.datetime.today()).delete()

        # Create a temporary directory we will create our archive in
        temp_directory = tempfile.mkdtemp()
        
        # We're going to create a list of file we need to put in the archive
        files = [os.path.join(temp_directory, "meta.json")]

        # Serialize the meta data and throw it into a file
        json.dump(task[1], open(files[0], "w"))

        for i in task[1]["submissions"]:
            sym_path = os.path.join(temp_directory, i["id"])
            os.symlink(os.path.join(SUBMISSION_DIRECTORY, i["id"]), sym_path)
            files.append(sym_path)



        archive_file = tempfile.mkstemp(suffix = ".tar.gz")[1]

        # Run tar and do the actual archiving. Will block until it's finished.
        return_code = subprocess.call(
            [
                "tar", "--dereference", "--create", "--gzip", "--directory",
                temp_directory, "--file", archive_file
            ] + [os.path.relpath(i, temp_directory) for i in files]
        )

        # Make the results available in the database
        archive = Archive.objects.get(id = ObjectId(task[0]))
        if return_code != 0:
            archive.error_string = \
                "tar failed with error code %d." % return_code
        else:
            archive.file_location = archive_file

        archive.expires = \
            datetime.datetime.today() + datetime.timedelta(hours = 2)

        archive.save()
        

@_api_call(("admin", "teacher"))
def get_submissions(current_user, assignment, email = None):
    """Creates an archive of students' submissions that a teacher or admin
    can download.
    
    :param assignment: The assignment that the retrieved submissions will be
                       for.
    :param email: The user that the retrieved submissions will be created by.
                 If none, all user's who submitted for the given assignment
                 will be retrieved.

    """
    
    query = {"assignment": ObjectId(assignment)}
    
    # If we were to always add user to the query, then mongo would search for
    # documents with email == None in the case that email equals None, which is
    # not desirable.
    if email:
        query["email"] = email
    
    submissions = list(Submission.objects(marked_for_grading = True, **query))
    
    if not submissions:
        return "No submissions found."

    # Form meta data on each submission that we will soon convert to JSON and
    # put inside of the archive we will send the user.
    submissions_meta = [
        {"id": str(i.id), "user": i.user, "timestamp": str(i.timestamp)}
            for i in submissions
    ]

    meta_data = {
        "query": {"assignment": assignment, "email": email},
        "submissions": submissions_meta
    }

    # Create a new entry in the database so we can track the progress of the
    # job.
    new_archive = Archive(requester = current_user.email)
    new_archive.save(force_insert = True)

    # Determine how many jobs are ahead of this one before we put it in the
    # queue.
    current_jobs = tar_tasks_queue.qsize()

    # We will not perform the work of archiving right now but will instead pass
    # if off to another thread to take care of it.
    tar_tasks_queue.put((new_archive.id, meta_data))

    # If the thread responsible for archiving is not running, start it up.
    global tar_tasks_thread
    if tar_tasks_thread is None or not tar_tasks_thread.is_alive():
        tar_tasks_thread = threading.Thread(name = "tar_tasks", target = tar_tasks)
        tar_tasks_thread.start()

    return ("Creating archive with id [%s]. Approximately %d jobs ahead of "
            "you. Access your archive by trying "
            "[Galah Domain]/archives/%s"
                % (str(new_archive.id), current_jobs, str(new_archive.id)))


from types import FunctionType
api_calls = dict((k, v) for k, v in globals().items() if isinstance(v, APICall))

if __name__ == "__main__":
    import json
    print get_api_info("current_user")