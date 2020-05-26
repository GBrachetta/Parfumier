"""sumary_line"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddReviewForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Post Review")


class EditReviewForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    edit_review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Update Review")
