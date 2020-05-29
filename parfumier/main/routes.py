"""sumary_line"""
from flask import Blueprint, url_for, redirect, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    DESCRIPTION
    """
    return redirect(url_for("perfumes.all_perfumes"))


@main.route("/about")
def about():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    return render_template("pages/index.html")
