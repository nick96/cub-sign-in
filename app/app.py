import logging
from functools import wraps

from celery import Celery
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_dance.contrib.google import google, make_google_blueprint
from forms import SignInForm, SignOutForm
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, TokenExpiredError
from werkzeug.contrib.fixers import ProxyFix

logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    app.config.from_envvar("CUB_SIGN_IN_CONFIG")
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


app = create_app()
celery = Celery("tasks", broker=app.config["CELERY_BROKER_URL"])

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    scope=["email", "profile"],
    offline=True,
)
app.register_blueprint(google_bp, url_prefix="/login")


def google_auth_required(handler):
    @wraps(handler)
    def f(*args, **kwargs):
        app.logger.debug("Checking if user is authorized")
        if not google.authorized:
            app.logger.debug(
                f"User is not authorized, redirection to {url_for('google.login')}"
            )
            return redirect(url_for("google.login"))

        return handler(*args, **kwargs)

    return f


def is_invited(email=None):
    app.logger.debug(f"Checking if {email} is on the invite list")
    if not email:
        app.logger.debug("User's email not given, getting from google")
        try:
            resp = google.get("oauth2/v2/userinfo")
        except (TokenExpiredError, InvalidClientIdError):
            app.logger.info("Token expired, redirecting user to page to renewal")
            return redirect(url_for("google.login"))
        if not resp.ok:
            app.logger.error(f"Failed to get {resp.url}: {resp.text}")
            abort(500)
        app.logger.info(f"Got {email} from user info request, session session value")
        email = resp.json()["email"]
        session["email"] = email
    else:
        app.logger.info("Email already set in session store")
    app.logger.debug(f"Checking if user with email {email} is invited")
    with open(app.config["INVITE_FILE"], "r") as f:
        invitees = [invitee.strip() for invitee in f.readlines()]
        return email in invitees


def invite_required(handler):
    @wraps(handler)
    def f(*args, **kwargs):
        app.logger.debug("Checking if user if invited")
        email = session.get("email")
        if not is_invited(email):
            app.logger.info(
                f"User with email {email} attempted login but are not invited"
            )
            abort(401)
        return handler(*args, **kwargs)

    return f


def get_autocomplete_data():
    if is_invited(session.get("email", "")):
        try:
            with open(app.config["NAMES_FILE"]) as f:
                return {name.strip(): None for name in f.readlines()}
        except FileNotFoundError:
            app.logger.info(
                f"{app.config['NAMES_FILE']} not found, so"
                + " kicking off the tak to populate it"
            )
            celery.send_task(
                "tasks.update_name_autocomplete",
                args=[
                    app.config["NAMES_FILE"],
                    app.config["SPREADSHEET_ID"],
                    [app.config["ROLL_SHEET"], app.config["NAMES_SHEET"]],
                ],
                kwargs={},
            )


@app.route("/")
@google_auth_required
def root():
    app.logger.debug(f"User is authorised, redirecting to {url_for('sign_in')}")
    return redirect(url_for("sign_in"))


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/sign-in", methods=["GET"])
@google_auth_required
def sign_in():
    form = SignInForm()
    return render_template(
        "form.html",
        is_sign_in=True,
        form_url=url_for("sign_in"),
        form=form,
        is_invited=is_invited(session.get("email")),
        autocomplete_data=get_autocomplete_data(),
    )


@app.route("/sign-out", methods=["GET"])
@google_auth_required
def sign_out():
    form = SignInForm()
    return render_template(
        "form.html",
        is_sign_in=False,
        form=form,
        is_invited=is_invited(session.get("email")),
        autocomplete_data=get_autocomplete_data(),
    )


@app.route("/sign-in", methods=["POST"])
@invite_required
@google_auth_required
def log_sign_in():
    form = SignInForm(request.form)
    if not form.validate_on_submit():
        app.logger.info("Sign in form not valid")
        app.logger.debug("Form: " + str(request.form))
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field: {error}")
        return redirect(url_for("sign_in"))

    celery.send_task(
        "tasks.add_sign_in",
        args=[
            form.cub_name.data,
            form.cub_signature.data,
            form.parent_signature.data,
            form.time.data,
            form.date.data,
            app.config["SPREADSHEET_ID"],
            app.config["ROLL_SHEET"],
        ],
        kwargs={},
    )
    return redirect(url_for("sign_in"))


@app.route("/sign-out", methods=["POST"])
@invite_required
@google_auth_required
def log_sign_out():
    """Record a sign in on the Google Sheet."""
    form = SignOutForm(request.form)
    if not form.validate_on_submit():
        app.logger.info("Sign out form not valid")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field)} field: {error}")
        return redirect(url_for("sign_out"))

    app.logger.debug("Sending sign out task")
    celery.send_task(
        "tasks.add_sign_out",
        args=[
            form.cub_name.data,
            form.parent_signature.data,
            form.time.data,
            form.date.data,
            app.config["SPREADSHEET_ID"],
            app.config["ROLL_SHEET"],
        ],
        kwargs={},
    )
    return redirect(url_for("sign_out"))


if __name__ == "__main__":
    app.run()
