import mongoengine
mongoengine.connect("galah")

# If were importing models from another component of galah the users shouldn't
# (and can't) be loaded.
try:
    from users import User
    from invitations import Invitation
except ImportError:
    pass

from classes import Class
from assignments import Assignment
from submissions import Submission
