import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo
from app.models import User
from app.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from app.utils import save_avatar

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="w",
    format="%(asctime)s %(name)s - %(filename)s :: %(lineno)d - %(levelname)s - %(message)s\n",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.route("/")
def index():
    """
    DESCRIPTION
    """
    return render_template("index.html")


@app.route("/about")
def about():
    """
    DESCRIPTION
    """
    return render_template("about.html", title="About")


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
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
                redirect(next_page) if next_page else redirect(url_for("index"))
            )
        else:
            flash("Please check your credentials", "warning")
    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        users.insert(
            {
                "username": form.username.data,
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": hashed_password,
                "is_admin": False,
                "avatar": "default.png",
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
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/account", methods=["POST", "GET"])
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
            avatar = save_avatar(form.avatar.data)
            old_value = mongo.db.users.find_one(
                {"username": current_user.username}
            )
            avatar = {"$set": {"avatar": avatar}}
            mongo.db.users.update_one(old_value, avatar)
            if current_user.avatar != "default.png":
                os.remove(
                    os.path.join(
                        app.root_path, "static/images", current_user.avatar
                    )
                )
        mongo.db.users.update_one(
            {"username": current_user.username}, {"$set": updated_user}
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
        flash("You have updated your information", "info")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.avatar.data = current_user.avatar
    avatar = url_for("static", filename=f"images/{current_user.avatar}")
    return render_template(
        "account.html", title="Account", form=form, avatar=avatar
    )


@app.route("/logout")
@login_required
def logout():
    """
    DESCRIPTION
    """
    logout_user()
    flash("We hope to see you back soon again!", "warning")
    return redirect(url_for("index"))


def send_reset_email(user):
    """
    DESCRIPTION
    """
    reset_user = User(
        username=user["username"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"],
        _id=user["_id"],
        is_admin=user["is_admin"],
        avatar=user["avatar"],
    )
    token = reset_user.get_reset_token()
    sender_email = os.environ.get("MAIL_USERNAME")
    password_email = os.environ.get("MAIL_PASSWORD")
    receiver_email = user["email"]
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = sender_email
    message["To"] = receiver_email
    receiver = mongo.db.users.find_one({"email": receiver_email})
    text = f"""You have requested to reset your password for your account on Parfumier.

To reset your password, please visit the following link:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.

Best regards,

Parfumier
"""
    html = f"""
    <html>
    <body>
    <h3>Dear <strong>{receiver['username']}</strong>,</h3><br>
       <p>You have requested to reset your password for your account on Parfumier.<br>
       <p>To reset your password, please visit the following link:<br><br>
       <a href="{url_for('reset_token', token=token, _external=True)}">Reset Password</a><br><br>
       If you did not make this request then simply ignore this email and no changes will be made.<br><br>
       Best Regards,<br>
       <em>Parfumier</em>
    </p>
    </body>
    </html>"""

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.strato.com", 465, context=context) as server:
        server.login(sender_email, password_email)
        server.sendmail(sender_email, receiver_email, message.as_string())


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        send_reset_email(user)
        flash("An email has been sent to reset your password", "success")
        return redirect(url_for("login"))
    return render_template(
        "reset_request.html", title="Reset Password", form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    """
    DESCRIPTION
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
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
        return redirect(url_for("login"))
    return render_template(
        "reset_token.html", title="Reset Password", form=form
    )


@app.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    """
    DESCRIPTION
    """
    mongo.db.users.remove({"username": current_user.username})
    logout_user()
    flash("You have deleted your account", "success")
    return redirect(url_for("index"))
