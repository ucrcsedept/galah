import web, config, re
from datetime import datetime
from pymongo.objectid import ObjectId
from mongoengine import *

from app.helpers import *
from app.models import *

def foo(i):
    try:
        return User.objects.get(email = i.email).checkPassword(i.password)
    except:
        import sys
        e = sys.exc_info()[1]
        print e

emailRe = re.compile(r".+@.+")
loginForm = web.form.Form(
    web.form.Textbox("email", description = "email", tabindex = 1),
    web.form.Password("password", description = "password", tabindex = 2),
    web.form.Button("submit", type="submit", html="Login", tabindex = 3),
    validators = [
        web.form.Validator("All fields are required",
            lambda i: i.email and i.password),
        web.form.Validator("You must enter a valid email address",
            lambda i: emailRe.match(i.email)),
        web.form.Validator("Incorrect email or password", foo)
    ]
)

registerForm = web.form.Form(
    web.form.Password("password", description = "password", tabindex = 1),
    web.form.Password("passwordConfirmation",
                      description = "password confirmation", tabindex = 2),
    web.form.Button("submit", type="submit", html="Login", tabindex = 3),
    validators = [
        web.form.Validator("All fields are required",
            lambda i: i.password and i.passwordConfirmation),
        web.form.Validator("Password fields do not match",
            lambda i: i.password == i.passwordConfirmation),
        web.form.Validator("Password must be greater than or equal to 5 characters",
            lambda i: len(i.password) >= 5)
    ]
)
registerFormRule = "Password must be greater than or equal to 5 characters, " \
                   "no other requirements exist."

class Register:
    def GET(self, zid):
        try:
            invitation = Invitation.objects.get(id = ObjectId(zid))
        except Invitation.DoesNotExist, ValueError:
            raise UserError("Invitation does not exist")
           
        if len(User.objects(email = invitation.email)) != 0:
            raise UserError("You cannot register twice")
            
        return config.view.register(invitation, registerForm(), registerFormRule)

    def POST(self, zid):
        try:
            invitation = Invitation.objects.get(id = ObjectId(zid))
        except Invitation.DoesNotExist, ValueError:
            raise UserError("Invitation does not exist")
        
        data = web.input()
        f = registerForm()
        
        if f.validates(data):
            newUser = User(email = invitation.email,
                           hash = User.createHash(data["password"]),
                           classes = [invitation.class_])
            newUser.save()
            
            raise web.seeother("/")
        else:
            return config.view.register(invitation, f, registerFormRule)
            

class Login:
    def _getRedirect(self, zdefault = "/"):
        redirect = \
            web.input().get("redirectTo", "/") or web.ctx.env.get("HTTP_REFERER")
        
        if not utils.isLocalUrl(redirect) or \
           redirect.startswith("/logout"):
            return zdefault
        else:
            return redirect
    
    def GET(self):
        f = loginForm()
            
        return config.view.login(self._getRedirect(), f)

    def POST(self):
        data = web.input()
        f = loginForm()
        
        if f.validates(data):
            auth.authenticate(data["email"])
            raise web.seeother(self._getRedirect())
        else:
            return config.view.login(self._getRedirect(), f)
    
class Logout:
    def GET(self):
        models.authentication.void()
        return config.view.logout()
