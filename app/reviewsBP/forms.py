from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddReviewForm(FlaskForm):
    review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Post Review")


class EditReviewForm(FlaskForm):
    review = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Update Review")
