import os
import secrets
from app import app, mongo
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
from app.models import User
from flask import url_for


def save_avatar(form_picture):
    """Saves avatar to file system

    Keyword arguments:
    argument -- description
    Return: returns a file to the file system with dimensions reduced
            as defined in the output size.
    """

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/images/avatars", picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    """Sends a multipart email using python email

    Keyword arguments:
    argument -- description
    Return: return_description
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
