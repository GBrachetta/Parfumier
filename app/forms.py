from app import mongo
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from flask_wtf import FlaskForm
from wtforms import(StringField, PasswordField, SubmitField, TextAreaField,
                    SelectMultipleField, FieldList, widgets, BooleanField)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name')
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.users.find_one({'username': username.data})
        if user:
            raise ValidationError('The username already exists.')

    def validate_email(self, email):
        user = mongo.db.users.find_one({'email': email.data})
        if user:
            raise ValidationError('The email already exists.')
