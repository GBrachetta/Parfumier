"""
Imports required for the below routes.
These include, besides all flask tools, the methods required to generate a
password hash, Cloudinary's imports to allow to upload the user avatar,
Mongodb, the User class, the necessary forms and the method from utils.py
used to send an email with a token to reset the password.
"""
from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from parfumier import mongo
from parfumier.models import User
from parfumier.users.forms import (
    LoginForm,
    RegistrationForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from parfumier.users.utils import send_reset_email


users = Blueprint("users", __name__)


@users.route("/login", methods=["POST", "GET"])
def login():
    """Logs the user in

    If the user is already authenticated, it redirects to the main route.
    Otherwise finds the user by the email address, and if the password matches
    the one in the database logs them in.
    It also uses the field 'remember me' to mantain the user in session.
    Uses the user_obj variable to log them in with flask_login, passing also
    that remember me boolean, and redirects to all the perfumes, habilitating
    the logged in user to interact with the database.
    In case the email or the password are incorrect or don't match, it
    redirects to the login page again with a warning message.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        if user and User.check_password(user["password"], form.password.data):
            user_obj = User(
                user["username"],
                user["first_name"],
                user["last_name"],
                user["email"],
                user["_id"],
                user["is_admin"],
                user["avatar"],
            )
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have logged in!", "info")
            return (
                redirect(next_page)
                if next_page
                else redirect(url_for("perfumes.all_perfumes"))
            )
        flash("Please check your credentials", "warning")
    return render_template("pages/login.html", title="Login", form=form)


@users.route("/register", methods=["POST", "GET"])
def register():
    """Registers a new user

    If the form validates (i.e. if the username and email are unique)
    a new user is created, assigning them by default a 'non-admin'
    status and a default avatar which can be changed later on.
    It also hashes the password.
    Finds the user after creating it and logs them immediately in.
    In case the form doesn't validate, it displays the corresponding
    validation errors.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    all_users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        all_users.insert(
            {
                "username": form.username.data.lower(),
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data.lower(),
                "password": hashed_password,
                "is_admin": False,
                "avatar": (
                    "https://res.cloudinary.com/gbrachetta/"
                    "image/upload/v1590003978/default.png"
                ),
            }
        )
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash(
            f"Account created for {form.username.data}. You are logged in.",
            "info",
        )
        return redirect(url_for("users.login"))
    return render_template("pages/register.html", title="Register", form=form)


@users.route("/account", methods=["POST", "GET"])
@login_required
def account():
    """Allows to edit the account information

    If the form passes validation, first checks if there is data in
    the image field. If there is, then uses cloudinary (again with
    the needed 'options' parameter) to upload, format and assign the
    user that image.
    Replaces http with https before recording the link in the document.
    Same as in the previous route, it finds the user and logs them in
    immediately after updating the account.
    Pre-populates the form with the current data from the database.
    """

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_uploaded = upload(form.avatar.data)
            # Options is a necessary parameter from Cloudinary in order to save
            # the thumbnails with the given settings.
            avatar, options = cloudinary_url(
                avatar_uploaded["public_id"],
                format="jpg",
                crop="fill",
                width=150,
                height=150,
            )
            avatar_link = avatar.replace("http", "https")
            old_value = mongo.db.users.find_one(
                {"username": current_user.username}
            )
            avatar = {"$set": {"avatar": avatar_link}}
            mongo.db.users.update_one(old_value, avatar)
        mongo.db.users.update_one(
            {"username": current_user.username},
            {
                "$set": {
                    "username": form.username.data.lower(),
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "email": form.email.data.lower(),
                }
            },
        )
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        # Creates user_obj to log user in immediately preventing a logout when
        # changing the key value in the class. Thanks to Yohan for this.
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash("You have updated your information", "info")
        return redirect(url_for("main.index"))
    # the if form.validate_on_submit() checks for method POST, so no
    # elif is needed to check for method GET after the return.
    form.username.data = current_user.username
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.email.data = current_user.email
    form.avatar.data = current_user.avatar
    avatar = current_user.avatar
    return render_template(
        "pages/account.html", title="Account", form=form, avatar=avatar
    )


@users.route("/logout")
@login_required
def logout():
    """Logs user out

    Uses logout_user from flask_login to log the user out.
    """

    logout_user()
    flash("We hope to see you back soon again!", "warning")
    return redirect(url_for("perfumes.all_perfumes"))


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    """Sends an email to reset password

    Using the method from the utils.py file, this route sends the user
    (if the email address exists) an email with a temporary token to reset
    their password in case they forgot it.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        send_reset_email(user)
        flash("An email has been sent to reset your password", "success")
        return redirect(url_for("users.login"))
    return render_template(
        "pages/reset_request.html", title="Reset Password", form=form
    )


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    """Resets the password

    Uses the method from utils.py to check for the validity of the token.
    If the token is valid, a form with two fields gives the user the
    possibility to create and confirm a new password, which similarly
    to the register account, will be hashed.
    Finds the user and logs them immediately in.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        mongo.db.users.update_one(
            {"email": user["email"]}, {"$set": {"password": hashed_password}}
        )
        user = mongo.db.users.find_one({"password": hashed_password})
        user_obj = User(
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["_id"],
            user["is_admin"],
            user["avatar"],
        )
        login_user(user_obj)
        flash("Your password has been updated. You are now logged in.", "info")
        return redirect(url_for("users.login"))
    return render_template(
        "pages/reset_token.html", title="Reset Password", form=form
    )


@users.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    """Deletes the current user

    Finds the current user in the database and removes it and
    logs it out.
    """

    mongo.db.users.remove({"username": current_user.username})
    logout_user()
    flash("You have deleted your account", "success")
    return redirect(url_for("main.index"))
