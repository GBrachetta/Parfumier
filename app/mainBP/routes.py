from flask import Blueprint, render_template

mainBP = Blueprint("mainBP", __name__)


@mainBP.route("/")
def index():
    """
    DESCRIPTION
    """
    return render_template("pages/index.html")
