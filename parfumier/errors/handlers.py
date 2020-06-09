"""
Imports only Blueprint and render_template in order to print
the required pages.
"""
from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    """
    Renders the corresponding page in case the error is found.
    The error code is passed and when met, triggers the method.
    """

    return render_template("errors/404.html", title="Page not found"), 404


@errors.app_errorhandler(403)
def error_403(error):
    """
    Renders the corresponding page in case the error is found.
    The error code is passed and when met, triggers the method.
    """
    return render_template("errors/403.html", title="Error 403"), 403


@errors.app_errorhandler(500)
def error_500(error):
    """
    Renders the corresponding page in case the error is found.
    The error code is passed and when met, triggers the method.
    """
    return render_template("errors/500.html", title="Error 500"), 500


@errors.app_errorhandler(405)
def error_405(error):
    """
    Renders the corresponding page in case the error is found.
    The error code is passed and when met, triggers the method.
    """
    return render_template("errors/405.html", title="Error 405"), 405
