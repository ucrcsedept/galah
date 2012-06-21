## Create the base form ##
from flask import request, url_for, render_template
from flaskext.wtf import Form, HiddenField
from werkzeug.exceptions import NotFound, HTTPException

class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        
        if not self.next.data:
            self.next.data = request.args.get("next") or request.referrer
        
        try:
            # Will raise an exception if no endpoint exists for the url
            app.create_url_adapter(request).match(self.next.data)
        except NotFound:
            self.next.data = ""
        except HTTPException:
            # Any other exceptions are harmless (I think)
            pass
    
    @property
    def redirect_target(self):
        return self.next.data

## Create the login form ##
from flask import redirect
from flaskext.wtf import Form, TextField, PasswordField, validators
from galah.db.models import User

class LoginForm(RedirectForm):
    email = TextField('Email', [validators.Required(), validators.Email()])
    password = PasswordField('Password', [validators.Required()])

# The actual view
from galahweb import app
from galah.db.crypto.passcrypt import check_seal, deserialize_seal
from galah.db.models import User
from flask.ext.login import login_user
from galahweb.auth import FlaskUser
from flask import redirect, url_for

@app.route("/login", methods = ["GET", "POST"])
@app.route("/", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    
    # If the user's input isn't immediately incorrect (validate_on_submit() will
    # not check if the email and password combo is valid, only that it could be
    # valid)
    # TODO: Verify this won't accept GET requests
    if form.validate_on_submit():
        # Find the user with the given email
        user = FlaskUser(User.objects.get(email = form.email.data))
        
        # Check if the entered password is correct
        if not check_seal(form.password.data, deserialize_seal(str(user.seal))):
            form.errors["global"] = ["Incorrect email + password combination."]
        else:
            login_user(user)
            return redirect(form.redirect_target or url_for("browse_assignments"))
    
    return render_template("login.html", form = form)
