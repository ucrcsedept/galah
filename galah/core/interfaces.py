def user_lookup(current_user, handle, _hints = None):
    """
    Quickly looks up information on a specific user.

    :param handle: The user's *exact* handle.
    :type handle: unicode

    :returns: A User object or ``None`` if no user was found.

    """

    pass

def user_multilookup(current_user, handles, _hints = None):
    """
    Quickly looks up information on a list of users.

    :param handles: A list of users' handles (must be exact like in
        user_lookup()).
    :type handles: list of unicode objects

    :returns: A list of User objects in no defined ordering. Any user that was
        not found will not appear in the list. If no users were found an empty
        list is returned.

    """

    pass

def user_find(current_user, handle_starts_with = None, role = None,
        in_class = None, _hints = None):
    """
    Searches for users with particular parameters. If multiple criteria are
    provided only users that satisfy *all* criteria will be returned.

    TODO: Document parameters when they're finalized.

    :returns: A generator that yields User objects.

    """

    pass

def user_create(current_user, new_user, _hints = None):
    """
    Creates a new user in the database. Raises an exception if user with the
    same handle exists.

    :param new_user: The user to add.
    :type new_user: User

    :returns: None

    """

    pass

def user_update(current_user, updated_user, _hints = None):
    """
    Updates a user object in the database.

    :param updated_user: The user object containing the updated values.
    :type update_user: User

    :returns: None

    """

    pass

def user_delete(current_user, handle, _hints = None):
    """
    Deletes a user object in the database.

    :param handle: The handle of the user to delete.
    :type handle: unicode

    :returns: None

    """

    pass

###############################################################################
########################## CLASSES ############################################
###############################################################################

def class_lookup(current_user, class_id, _hints = None):
    """
    Quickly looks up information on a particular class.

    :param class_id: The ID of the class to lookup.
    :type class_id: Class.ID

    :returns: A Class or None if no matching class was found.

    """

    pass

def class_multilookup(current_user, class_ids, _hints = None):
    """
    Quickly looks up information on a number of different classes.

    :param class_ids: A list of class ids (must be exact like in
        user_lookup()).

    :returns: A list of Class objects in no defined ordering. Any class that
        was not found will not appear in the list. If no classes were found an
        empty list is returned.

    """

    pass

def class_find(current_user, term, handle_starts_width, _hints = None):
    pass

def class_create(current_user, new_class, _hints = None):
    pass

def class_update(current_user, updated_class, _hints = None):
    pass

def class_delete(current_user, id, _hints = None):
    pass

###############################################################################
########################## ASSIGNMENTS ########################################
###############################################################################

def assignment_lookup(current_user, assignment_id, _hints = None):
    pass

def assignment_find(current_user, for_classes = None, _hints = None):
    pass

def assignment_create(current_user, new_assignment, _hints = None):
    pass

def assignment_delete(current_user, id, _hints = None):
    pass

###############################################################################
########################## SUBMISSIONS ########################################
###############################################################################

def submission_lookup(current_user, submission_id, _hints = None):
    pass

def submission_find(current_user, author = None, for_assignment = None,
        _hints = None):
    pass

def submission_create(current_user, new_submission, _hints = None):
    pass

def submission_update(current_user, updated_submission, _hints = None):
    pass

def submission_delete(current_user, submission_id, _hints = None):
    pass

###############################################################################
########################## TESTREQUESTS #######################################
###############################################################################

def testrequest_lookup(current_user, testrequest_id, _hints = None):
    pass

def testrequest_pop(current_user, _hints = None):
    pass

def testrequest_create(current_user, new_testrequest, _hints = None):
    pass

def testrequest_delete(current_user, testrequest_id, _hints = None):
    pass

###############################################################################
########################## TESTRESULTS ########################################
###############################################################################

def testresult_lookup(current_user, testresult_id, _hints = None):
    pass

def testresult_find(current_user, for_submission = None, for_user = None,
        for_assignment = None, _hints = None):
    pass

def testresult_create(current_user, new_testresult, _hints = None):
    pass

def testresult_update(current_user, updated_testresult, _hints = None):
    pass

def testresult_delete(current_user, testresult_id, _hints = None):
    pass

###############################################################################
########################## TASKS ##############################################
###############################################################################

def task_lookup(current_user, task_id, _hints = None):
    pass

def task_create(current_user, new_task, _hints = None):
    pass

def task_pop(current_user, action, _hints = None):
    pass

def task_delete(current_user, task_id, _hints = None):
    pass
