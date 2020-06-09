"""Imports needed for the forms. Types of fields and validators"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class AddReviewForm(FlaskForm):
    """Form to add a review

    In addition to its 2 fields it has a custom validator.
    Since CKEditor (my WYSIWYG editor for text fields) creates
    html, DataRequired() isn't enough to check for an empty
    text field, so this custom validator replaces all html
    with empty strings to allow for an accurate validation
    error in case the user attempts to enter an empty review.
    """

    review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Post Review")

    def validate_review(self, review):
        text = (
            review.data.replace("<p>", "")
            .replace("</p>", "")
            .replace("&nbsp; ", "")
            .replace("&nbsp;", "")
            .replace("&ensp;", "")
            .replace("&emsp;", "")
            .replace("<br>", "")
        )
        if not text:
            raise ValidationError("You cannot enter a blank review.")


class EditReviewForm(FlaskForm):
    """Form to edit a review

    Similar to the one above
    """

    edit_review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Update Review")
