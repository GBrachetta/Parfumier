"""Imports Blueprints, url_for and redirect to divert to the all_perfumes route
and render_template to display the about page"""
from flask import Blueprint, url_for, redirect, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    Redirects to all perfumes, so user lands directly
    having an overview of all the perfumes in the database.
    """
    return redirect(url_for("perfumes.all_perfumes"))


@main.route("/about")
def about():
    """Renders the about page with general information"""

    return render_template("pages/about.html", title="About")
