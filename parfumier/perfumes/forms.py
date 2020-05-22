"""sumary_line"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField,
)
from wtforms.validators import DataRequired


class CreatePerfumeForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    brand = StringField("Brand", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    public = BooleanField("Public")
    submit = SubmitField("Create")
    picture = FileField("Picture", validators=[FileAllowed(["jpg", "png"])])
    perfume_type = StringField("Type", validators=[DataRequired()])


class EditPerfumeForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    brand = StringField("Brand", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    public = BooleanField("Public")
    submit = SubmitField("Update")
    picture = FileField("Picture", validators=[FileAllowed(["jpg", "png"])])
    perfume_type = StringField("Type", validators=[DataRequired()])


class SearchForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    choices = [("Brand", "Brand"), ("Perfume", "Perfume"), ("Type", "Type")]
    select = SelectField("Search:", choices=choices)
    search = StringField("")
