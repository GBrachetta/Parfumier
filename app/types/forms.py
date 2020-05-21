from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from app import mongo


class CreateTypeForm(FlaskForm):
    type_name = StringField("Type", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Create")

    def validate_type_name(self, type_name):
        """
        DESCRIPTION
        """
        typeName = mongo.db.types.find_one({"type_name": type_name.data})
        if typeName:
            raise ValidationError("The type already exists.")


class EditTypeForm(FlaskForm):
    origin_type_name = HiddenField()
    type_name = StringField("Type", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Update")
    # https://stackoverflow.com/questions/61896450/check-duplication-when-edit-an-exist-database-field-with-wtforms-custom-validato

    def validate_type_name(self, type_name):
        typeName = mongo.db.types.find_one({"type_name": type_name.data})
        if typeName and type_name.data != self.origin_type_name.data:
            raise ValidationError("The type already exists")
