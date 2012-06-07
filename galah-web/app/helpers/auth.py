import web.session, config, os, re

from bson.objectid import ObjectId

_objectid_re = re.compile("[A-Fa-f0-9]{24}")
_session = web.session.Session(
    config.app, 
    web.session.DiskStore("/var/local/galah-web/sessions")
)
        

def authenticated():
    """
    Returns the ObjectId of the authenticated user, or None if no user has been
    authenticated.
    
    """
    
    return _session.get("user", None)
    
def authenticate(zuser):
    _session["user"] = zuser
    
def void():
    if "user" in _session:
        del _session["user"]

def authenticationRequired(zfunc, zuserType = None):
    def inner(*zargs, **zkwargs):
        if not authenticated():
            raise web.seeother("/login?redirectTo=%s" % web.ctx.path)
        
        return zfunc(*zargs, **zkwargs)
        
    return inner
