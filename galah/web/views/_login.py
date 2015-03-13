## Create the base form ##
from flask import request, url_for, render_template
from flask.ext.wtf import Form
from wtforms.fields import HiddenField
from galah.web.util import is_url_on_site, GalahWebAdapter

# Load up the configuration to get email validation regular expression
from galah.base.config import load_config
config = load_config("web")

import logging

logger = GalahWebAdapter(logging.getLogger("galah.web.views.login"))

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
from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField
import wtforms.validators as validators
from galah.db.models import User

class LoginForm(RedirectForm):
    email = TextField("Email",
                      [validators.Required(),
                       validators.regexp(config["EMAIL_VALIDATION_REGEX"])])
    password = PasswordField("Password", [validators.Required()])

# The actual view
from galah.web import app, oauth_enabled
from galah.base.crypto.passcrypt import check_seal, deserialize_seal
from galah.db.models import User
from flask.ext.login import login_user
from galah.web.auth import FlaskUser
from flask import redirect, url_for, flash, request

# Google OAuth2
from oauth2client.client import OAuth2WebServerFlow

# Google OAuth2 flow object to get user's email.
if oauth_enabled:
    flow = OAuth2WebServerFlow(
        client_id = app.config["GOOGLE_SERVERSIDE_ID"],
        client_secret = app.config["GOOGLE_SERVERSIDE_SECRET"],
        scope = "https://www.googleapis.com/auth/userinfo.email",
        redirect_uri = app.config["HOST_URL"] + "/oauth2callback"
    )

@app.route("/login/", methods = ["GET", "POST"])
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

        if oauth_enabled and user and not user.seal:
            flash("You must use R'Mail to login.", category = "error")

            logger.info(
                "User %s has tried to log in via internal auth but their "
                "account does not have a seal.", user.email
            )

            return render_template(
                "login.html", form = form, oauth_enabled = oauth_enabled
            )

        # Check if the entered password is correct
        if not user or \
                not check_seal(form.password.data, deserialize_seal(str(user.seal))):
            flash("Incorrect email or password.", category = "error")

            logger.info(
                "User %s has entered an incorrect email/password pair during "
                "internal auth.", form.email.data
            )
        else:
            login_user(user)

            logger.info(
                "User %s has succesfully logged in via internal auth.",
                user.email
            )

            return redirect(form.redirect_target or url_for("browse_assignments"))
    elif oauth_enabled and request.args.get("type") == "rmail":
        # Login using Google OAuth2
        # Step 1 of two-factor authentication: redirect to AUTH url
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    return render_template(
        "login.html",
        form = form,
        oauth_enabled = oauth_enabled,
        google_login_heading = app.config["GOOGLE_LOGIN_HEADING"],
        google_login_caption = app.config["GOOGLE_LOGIN_CAPTION"]
    )

@app.route("/oauth2callback/")
def authenticate_user():
    """
    Authenticate user as logged in after Google OAuth2 sends a callback.

    """

    error = request.args.get("error")
    if error:
        logger.warning("Google sent us an error via OAuth2: %s", error)

        return redirect(url_for("login"))

    # Get OAuth2 authentication code
    code = request.args.get("code")

    # Exchange code for fresh credentials
    credentials = flow.step2_exchange(code)

    # Extract email and email verification
    id_token = credentials.id_token
    email = id_token["email"]
    verified_email = id_token["email_verified"]

    if verified_email is True:
        # Find the user with the given email
        try:
            user = FlaskUser(User.objects.get(email = email))
        except User.DoesNotExist:
            user = None

        if not user:
            flash("A Galah account does not exist for this email.", "error")

            logger.info(
                "User %s has attempted to log in via OAuth2 but an account "
                "does not exist for them.", email
            )
        else:
            login_user(user)

            logger.info(
                "User %s has succesfully logged in via OAuth2.", email
            )

            return redirect(url_for("home"))

    else:
        flash("Sorry, we couldn't verify your email", "error")

        logger.info("User %s failed to authenticate with OAuth2 because "
            "their email has not been verified with google.", email)

    return redirect(url_for("login"))
