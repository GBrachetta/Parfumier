"""Imports with fields and validators required for the forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed
from parfumier import mongo


class CreateTypeForm(FlaskForm):
    """Form to create a perfume type

    Includes the three needed fields and validator
    """

    type_name = StringField("Type Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    type_picture = FileField(
        "Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )
    submit = SubmitField("Create")

    def validate_type_name(self, type_name):
        """
        This custom validator queries the database to check if the
        perfume type already exists in the database.
        """
        existing_type = mongo.db.types.find_one({"type_name": type_name.data})
        if existing_type:
            raise ValidationError("The type already exists.")


class EditTypeForm(FlaskForm):
    """Form to edit an existing perfume type

    Similar to the one above, with the adition of an extra
    hidden field explaned below.
    """

    origin_type_name = HiddenField()
    type_name = StringField("Type", validators=[DataRequired()])
    description = TextAreaField("Description")
    type_picture = FileField(
        "Picture", validators=[FileAllowed(["jpg", "jpeg", "png"])]
    )
    submit = SubmitField("Update")
    # https://stackoverflow.com/questions/61896450/check-duplication-when-edit-an-exist-database-field-with-wtforms-custom-validato

    def validate_type_name(self, type_name):
        """Custom validator

        Thanks to the hidden field acquiring the current value of the
        type_name field, this validator can check for repeated perfume types
        while not throwing a validation error in case the type is the type
        being edited. (i.e. in case the user wants to edit the description
        of the perfume while mantaining the current name, in which case
        the validator allows that particular 'duplication').
        """

        existing_type = mongo.db.types.find_one({"type_name": type_name.data})
        if existing_type and type_name.data != self.origin_type_name.data:
            raise ValidationError("The type already exists")
