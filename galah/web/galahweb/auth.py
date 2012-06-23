# Wrapper around User to allow Flask-Login to work with it
from types import MethodType
def FlaskUser(user):
    "Decorates a given User instance with the methods in the UserMixin class"
    
    methodize = lambda func: MethodType(func, user)
    
    # Too many problems were occuring transplanting the UserMixin class so I
    # remade the methods here.
    user.is_active = methodize(lambda self: True)
    user.is_authenticated = methodize(lambda self: True)
    user.is_anonymous = methodize(lambda self: True)
    user.get_id = methodize(lambda self: self.id)
    
    return user

# All users must have an account_type variable in order for the 
# account_type_required decorator to work
from flask.ext.login import AnonymousUser
class Anonymous(AnonymousUser):
    account_type = None

## Decorator that enforces account_type based permissions ##
from functools import wraps
from flask.ext.login import current_user
from flask import current_app, flash
def account_type_required(account_type):
    def internal_decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated() or \
               current_user.account_type != account_type:
                flash("Only %s users are permitted to access this page."
                          % account_type)
                return current_app.login_manager.unauthorized()
                
            return func(*args, **kwargs)
        
        return decorated_view
        
    return internal_decorator

# Set up the login manager
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = None
    
# Loads a user useable by Flask-Login from a user id (email)
from galah.db.models import User
@login_manager.user_loader
def load_user(email):
    return FlaskUser(User.objects.get(email = email))
