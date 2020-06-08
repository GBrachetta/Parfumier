"""sumary_line"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Email,
    Length,
    ValidationError,
    Regexp,
)
from flask_login import current_user
from parfumier import mongo


class RegistrationForm(FlaskForm):
    """
    DESCRIPTION
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            Regexp(
                "^\\w+$",
                message="Only letters, numbers and underscores are allowed.",
            ),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be 8 characters long"),
            Regexp(
                "^(?=.*?[A-Za-z])", message="Password must contain a letter.",
            ),
            Regexp(
                "^(?=.*?[0-9])", message="Password must contain a number.",
            ),
            Regexp(
                "^(?=.*?[#?!@$%^&*-])",
                message="Password must contain a special character.",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        """
        DESCRIPTION
        """
        user = mongo.db.users.find_one({"username": username.data.lower()})
        if user:
            raise ValidationError("The username already exists.")

    def validate_email(self, email):
        """
        DESCRIPTION
        """
        user = mongo.db.users.find_one({"email": email.data.lower()})
        if user:
            raise ValidationError("The email already exists.")


class LoginForm(FlaskForm):
    """
    DESCRIPTION
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    """
    DESCRIPTION
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            Regexp(
                "^\\w+$",
                message="Only letters, numbers and underscores are allowed.",
            ),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    avatar = FileField(
        "Choose Avatar", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )

    submit = SubmitField("Update")

    def validate_username(self, username):
        """
        DESCRIPTION
        """
        if username.data.lower() != current_user.username:
            user = mongo.db.users.find_one({"username": username.data.lower()})
            if user:
                raise ValidationError("The username already exists.")

    def validate_email(self, email):
        """
        DESCRIPTION
        """
        if email.data.lower() != current_user.email:
            user = mongo.db.users.find_one({"email": email.data.lower()})
            if user:
                raise ValidationError("The email already exists.")


class RequestResetForm(FlaskForm):
    """
    DESCRIPTION
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        """
        DESCRIPTION
        """
        user = mongo.db.users.find_one({"email": email.data.lower()})
        if user is None:
            raise ValidationError("There is no accout with that email.")


class ResetPasswordForm(FlaskForm):
    """
    DESCRIPTION
    """

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be 8 characters long."),
            Regexp(
                "^(?=.*?[A-Za-z])", message="Password must contain a letter.",
            ),
            Regexp(
                "^(?=.*?[0-9])", message="Password must contain a number.",
            ),
            Regexp(
                "^(?=.*?[#?!@$%^&*-])",
                message="Password must contain a special character.",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Reset Password")
