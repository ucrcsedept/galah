def user_lookup(current_user, handle, _hints = None):
    """
    :param handle: The handle of the user to look up.

    :returns: A User object or ``None`` if user was found.

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
    pass

def user_update(current_user, updated_user, _hints = None):
    pass

def user_delete(current_user, handle, _hints = None):
    pass

###############################################################################
########################## CLASSES ############################################
###############################################################################

def class_lookup(current_user, class_id, _hints = None):
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

def testrequest_update(current_user, updated_testrequest, _hints = None):
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
