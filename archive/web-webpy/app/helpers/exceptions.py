class UserError(Exception):
    "An error that occurs because the user did something wrong."
    
    def __init__(self, zmessage):
        Exception.__init__(self, zmessage)
