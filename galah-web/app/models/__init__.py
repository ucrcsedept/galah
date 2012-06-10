import mongoengine
mongoengine.connect("galah")

from classes import Class
from users import User
from invitations import Invitation
from assignments import Assignment
from submissions import Submission
