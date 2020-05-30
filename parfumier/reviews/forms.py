"""sumary_line"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class AddReviewForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Post Review")

    def validate_review(self, review):
        text = (
            review.data.replace("<p>", "")
            .replace("</p>", "")
            .replace("&nbsp;", "")
            .replace("&ensp;", "")
            .replace("&emsp;", "")
            .replace("<br>", "")
        )
        if not text:
            raise ValidationError(
                "Please enter content in your review."
            )


class EditReviewForm(FlaskForm):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    edit_review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Update Review")
