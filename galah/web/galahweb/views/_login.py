## Create the base form ##
from flask import request, url_for, render_template
from flaskext.wtf import Form, HiddenField
from galah.web.galahweb.util import is_url_on_site

class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        
        if not self.next.data:
            self.next.data = request.args.get("next") or request.referrer
        
        if not is_url_on_site(app, self.next.data):
            self.next.data = ""
    
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
from galah.web.galahweb import app
from galah.db.crypto.passcrypt import check_seal, deserialize_seal
from galah.db.models import User
from flask.ext.login import login_user
from galah.web.galahweb.auth import FlaskUser
from flask import redirect, url_for, flash

@app.route("/login", methods = ["GET", "POST"])
@app.route("/", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    
    # If the user's input isn't immediately incorrect (validate_on_submit() will
    # not check if the email and password combo is valid, only that it could be
    # valid)
    if form.validate_on_submit():
        # Find the user with the given email
        try:
            user = FlaskUser(User.objects.get(email = form.email.data))
        except User.DoesNotExist:
            user = None
        
        # Check if the entered password is correct
        if not user or \
           not check_seal(form.password.data, deserialize_seal(str(user.seal))):
            flash("Incorrect email or password.", category = "error")
        else:
            login_user(user)
            return redirect(form.redirect_target or url_for("browse_assignments"))
    
    app.logger.debug(str(form.errors))
    
    return render_template("login.html", form = form)
