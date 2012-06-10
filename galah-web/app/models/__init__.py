import mongoengine
mongoengine.connect("galah")

# If were importing models from another component of galah the users shouldn't
# (and can't) be loaded.
try:
    from users import User
except ImportError:
    pass

from classes import Class
from invitations import Invitation
from assignments import Assignment
from submissions import Submission
