"""
Imports the required tools, including fields, validators, mongodb
and flask_login current_user to identify them
"""
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
    """Form to allow for the registration of a new user

    Includes its fields and validators, inluding a minimum and maximum
    length for the username, and also forbidding spaces and characters
    other than letters, numbers and underscores using regex.
    Several validators put in place to require a length, at least a letter,
    a number and a special character for the password in order to ensure
    a strong one.
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
        """Custom validator

        It checks the database to prevent the creation of a
        duplicate (already existing) username.
        """

        user = mongo.db.users.find_one({"username": username.data.lower()})
        if user:
            raise ValidationError("The username already exists.")

    def validate_email(self, email):
        """Custom validator

        Same as the one above, this one prevents the creation
        of an email address already present in the database,
        specially relevant since users log in using this field.
        """

        user = mongo.db.users.find_one({"email": email.data.lower()})
        if user:
            raise ValidationError("The email already exists.")


class LoginForm(FlaskForm):
    """Form to log in user

    Includes DataRequired validators for its corresponding fields.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    """Form to edit and update account information

    Similar to the register form, this includes a regex validator to
    only allow for letters, numbers and underscores in case the user
    wants to edit and update their username.
    The avatar field only allows for basic image formats.
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
        "Avatar", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )

    submit = SubmitField("Update")

    def validate_username(self, username):
        """Custom validator

        Checks if the user wants to update their username and if it's different
        from the current one, raises a validation error in case
        that username already exists in the dabase.
        It uses flask_login to check the data in current_user.
        """

        if username.data.lower() != current_user.username:
            user = mongo.db.users.find_one({"username": username.data.lower()})
            if user:
                raise ValidationError("The username already exists.")

    def validate_email(self, email):
        """Custom validator

        Similar to the one above, checks for duplicated email addresses
        in the database in case the user wishes to change their current one.
        """

        if email.data.lower() != current_user.email:
            user = mongo.db.users.find_one({"email": email.data.lower()})
            if user:
                raise ValidationError("The email already exists.")


class RequestResetForm(FlaskForm):
    """Form to request a password reset

    Only two fields are required for this form, with its necessary validators.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        """Custom validator

        Queries the database to check if the email exists.
        If it doesn't, it raises a validation error warning about it.
        """

        user = mongo.db.users.find_one({"email": email.data.lower()})
        if user is None:
            raise ValidationError("There is no accout with that email.")


class ResetPasswordForm(FlaskForm):
    """Form to reset password

    Similar to the one used in the register user route, this one
    also has several validators in place to permit only passwords
    that match certain requirements.
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
