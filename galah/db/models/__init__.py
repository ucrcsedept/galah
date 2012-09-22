import mongoengine

# If were importing models from another component of galah the users shouldn't
# (and can't) be loaded.
try:
    import users
    from users import User
    
    import invitations
    from invitations import Invitation
except ImportError:
    pass

import classes
from classes import Class

import assignments
from assignments import Assignment

import submissions
from submissions import Submission

import archives
from archives import Archive
