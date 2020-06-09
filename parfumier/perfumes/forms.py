"""Imports form-related items, types of fields
and items related with importing files"""
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
    """Form to create new perfumes

    Includes validators, and allows for certain types of image files
    only to be uploaded in the picture field.
    """

    brand = StringField("Brand", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    public = BooleanField("Public")
    submit = SubmitField("Create")
    picture = FileField(
        "Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )
    perfume_type = StringField("Type", validators=[DataRequired()])


class EditPerfumeForm(FlaskForm):
    """Form to edit perfumes

    Same validators as the previous one.
    """

    brand = StringField("Brand", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    public = BooleanField("Public")
    submit = SubmitField("Update")
    picture = FileField(
        "Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )
    perfume_type = StringField("Type", validators=[DataRequired()])


class SearchForm(FlaskForm):
    """Form allowing to seach through the databse

    Allows to search by brand, Perfume name and type of perfume.
    The corresponding route deals with indexing the aggregate
    through all these three fields.
    """

    choices = [("Brand", "Brand"), ("Perfume", "Perfume"), ("Type", "Type")]
    select = SelectField("Search:", choices=choices)
    search = StringField("")
