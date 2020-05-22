from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    DESCRIPTION
    """
    return render_template("pages/index.html")
