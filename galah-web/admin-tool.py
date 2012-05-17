from optparse import OptionParser, make_option

from app.models.users import User

## Handle Command Line Arguments ##
optionList = [
    make_option("--add-user", dest = "inviteAdmin",
                metavar = "EMAIL[,TYPE,PASS]", type = "str",
                help = "If PASS is not provided an email will be sent to EMAIL "
                       "with an invitation to register. If PASS is provided a "
                       "new user is created with that password. In either case "
                       "the user will recieve an account with the given type."),
    make_option("--set-user-type", dest = "setUserType", metavar = "EMAIL,TYPE",
                type
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
        return int(zaccountType)
    except ValueError:
        try:
            return User.accountTypes[zaccountType]
        except KeyError:
            print >> sys.stderr, zaccountType, "is not a valid account type"
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

## Invite Admin ##
def inviteAdmin(zemail, zaccountType = None, zpassword = None):
    import re, app.models.users, app.models.invitations
    
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
        
        print "Create user: {email: %s, hash: %s, accountType: %s}" % \
                  (zemail, hash, User.accountTypes.getName(zaccountType))
    else:
        raise NotImplementedError
        
    return True

if cmdOptions.inviteAdmin:
    inviteAdmin(*cmdOptions.inviteAdmin.split(","))
