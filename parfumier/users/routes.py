"""
Docstring
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
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
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
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    all_users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        all_users.insert(
            {
                "username": form.username.data,
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": hashed_password,
                "is_admin": False,
                "avatar": (
                    "https://res.cloudinary.com/gbrachetta/"
                    "image/upload/v1590003978/default.png"
                ),
            }
        )
        user = mongo.db.users.find_one({"email": form.email.data})
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
            f"Account created for {form.username.data}. You are now logged in.",
            "info",
        )
        return redirect(url_for("users.login"))
    return render_template("pages/register.html", title="Register", form=form)


@users.route("/account", methods=["POST", "GET"])
@login_required
def account():
    """
    DESCRIPTION
    """
    form = UpdateAccountForm()
    updated_user = {
        "username": form.username.data,
        "first_name": form.first_name.data,
        "last_name": form.last_name.data,
        "email": form.email.data,
    }
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
            old_value = mongo.db.users.find_one(
                {"username": current_user.username}
            )
            avatar = {"$set": {"avatar": avatar}}
            mongo.db.users.update_one(old_value, avatar)
        mongo.db.users.update_one(
            {"username": current_user.username}, {"$set": updated_user}
        )
        user = mongo.db.users.find_one({"email": form.email.data})
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
    """
    DESCRIPTION
    """
    logout_user()
    flash("We hope to see you back soon again!", "warning")
    return redirect(url_for("perfumes.all_perfumes"))


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        send_reset_email(user)
        flash("An email has been sent to reset your password", "success")
        return redirect(url_for("users.login"))
    return render_template(
        "pages/reset_request.html", title="Reset Password", form=form
    )


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    """
    DESCRIPTION
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
    """
    DESCRIPTION
    """
    mongo.db.users.remove({"username": current_user.username})
    logout_user()
    flash("You have deleted your account", "success")
    return redirect(url_for("main.index"))
