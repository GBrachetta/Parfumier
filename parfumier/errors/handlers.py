from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template("errors/404.html", title="Page not found"), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template("errors/403.html", title="Page not found"), 403


@errors.app_errorhandler(500)
def error_500(error):
    return render_template("errors/500.html", title="Page not found"), 500


@errors.app_errorhandler(405)
def error_405(error):
    return render_template("errors/405.html", title="Page not found"), 405
