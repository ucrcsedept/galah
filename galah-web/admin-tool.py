from optparse import OptionParser, make_option

import config, sys
from app.models.users import User
from mongoengine import *

## Handle Command Line Arguments ##
optionList = [
    make_option("--add-user", dest = "inviteAdmin",
                metavar = "EMAIL[,TYPE,PASS]", type = "str",
                help = "If PASS is not provided an email will be sent to EMAIL "
                       "with an invitation to register. If PASS is provided a "
                       "new user is created with that password. In either case "
                       "the user will recieve an account with the given type."),
    make_option("--find-user", dest = "findUser", metavar = "QUERY", type = str,
                help = "[Documentation missing, maybe you'd like to add it?]"),
    make_option("--create-class", dest = "createClass",
                metavar = "NAME,INSTRUCTOR[,INSTRUCTOR,...]", type = str,
                help = "[Documentation missing, maybe you'd like to add it?]")
]

parser = OptionParser(
    description = "Facilitates administrative tasks concerning galah-web that "
                  "can't be done through the online interface.",
    option_list = optionList)

cmdOptions = parser.parse_args()[0]

## Globally Useful Functions ##
def isEmail(zobject):
    import re
    
    if not isinstance(zobject, basestring):
        return False
        
    return re.match(".+@.+", zobject) != None

def toAccountNum(zobject):
    try:
        return int(zobject)
    except ValueError:
        try:
            return User.accountTypes[zobject]
        except KeyError:
            print >> sys.stderr, zobject, "is not a valid account type"
            raise ValueError

# Follow these conventions when adding tasks:
#   * Prefix each block of code containing logic for a task with a comment
#     header of the form *## TASK DESCRIPTION ##*
#   * Seperate the logic that dissects the raw input from the user from the task
#     logic by putting the task logic inside of its own function and using a
#     simple conditional to call it, see below for an example. **Reasoning:**
#     I want this admin-tool to be importable and it should also make the code
#     a little more structured and thusly more readable.
#   * Perform all imports in a local scope, we should avoid having a huge list
#     of imports at the top of this file as it could get large very quickly and
#     keeping track of what needs what will be tedious. The loss in speed that
#     results is not really an issue.
#   * Do your best not to throw exceptions that go uncaught, if a task can't be
#     completed the other tasks should continue unfazed.
#   * Print a confirmation that your task completed successfully or failed.
#   * Whenever you print anything to the screen prefix the message with the name
#     of the task your doing (ex: inviteAdmin).

## Invite Admin ##
def inviteAdmin(zemail, zaccountType = None, zpassword = None):
    import app.models.users, app.models.invitations
    
    if zaccountType == None:
        zaccountType = User.accountTypes.student
    
    try:
        zaccountType = toAccountNum(zaccountType)
    except ValueError:
        return False
        
    if zpassword:
        hash = User.createHash(zpassword)
        
        newUser = User(email = zemail,
                       hash = hash,
                       accountType = zaccountType)
        newUser.save()
        
        print "inviteAdmin: Created user {email: %s, hash: %s, accountType: %s}" % \
                  (zemail, hash, User.accountTypes.getName(zaccountType))
    else:
        raise NotImplementedError
        
    return True

if cmdOptions.inviteAdmin:
    inviteAdmin(*cmdOptions.inviteAdmin.split(","))
    
## Find User ##
def findUser(zquery):
    from app.models import User
    from pymongo.objectid import ObjectId
    from bson.errors import InvalidId
    from app.helpers.utils import Enum
    import re, sys
    
    SearchTypes = Enum("email account inClass")
    searchType = None
    queryValue = None
    
    # Try to figure out what they're searching by
    if searchType is None:                    
        if re.match(".*@.*", zquery):
            searchType = SearchTypes.email
            queryValue = str(zquery)
        elif re.match("[A-Fa-f0-9]{24}$", zquery):
            searchType = SearchTypes.inClass
            queryValue = ObjectId(zquery)
        elif re.match("[0-2]$", zquery):
            searchType = SearchTypes.account
            queryValue = int(zquery)
    
    if searchType is None:
        print >> sys.stderr, "findUser: Cannot understand search query"
        return False
    else:
        print "findUser: Searching by", SearchTypes.getName(searchType)
    
    searchTypeToKey = {
        SearchTypes.email: "_id",
        SearchTypes.account: "accountType",
        SearchTypes.inClass: "classes"
    }
    
    results = \
        list(User.objects(__raw__ = {searchTypeToKey[searchType]: queryValue}))
    
    print "findUser: Found", len(results), "users matching your query:"
    for i in results:
        print "%s (%s)" % (i.email, User.accountTypes.getName(i.accountType))

    return True
    
if cmdOptions.findUser:
    findUser(cmdOptions.findUser)
    
## Create Class ##
def createClass(zname, zinstructors):
    from app.models import Class, User
    
    instructors = []
    for i in zinstructors:
        try:
            instructor = User.objects.get(email = i)
        except Exception as e:
            # STUPID hacky but for some reason can't figure out where the
            # DoesNotExist and MultipleObjectsReturned are for the life of me.
            # If you can fix this I will be very very thankful.
            if repr(e).startswith("DoesNotExist("):
                print >> sys.stderr, "createClass:", i, " does not exist."
                return False
            else:
                raise
        
        if instructor.accountType != User.accountTypes.instructor:
            print >> sys.stderr, "createClass:", i, "is not an instructor"
            return False
            
        instructors.append(instructor)
        
    newClass = Class(name = zname)
    newClass.save()
    
    for i in instructors:
        i.classes.append(newClass)
        i.save()
        
    print "createClass: Succesfully created class"
    
    return True
    
if cmdOptions.createClass:
    args = cmdOptions.createClass.split(",")
    
    if len(args) < 2:
        print >> sys.stderr, "createClass: Class must have at least one instructor"
    else:
        if not createClass(args[0], args[1:]):
            print >> sys.stderr, \
                "createClass: Aborted, no changes written to db"
