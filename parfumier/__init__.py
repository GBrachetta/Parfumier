"""sumary_line"""
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from parfumier.config import Config


login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Please log in."
login_manager.login_message_category = "info"
mongo = PyMongo()


def create_app(config_class=Config):
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    login_manager.init_app(app)
    mongo.init_app(app)
    from parfumier.users.routes import users
    from parfumier.perfumes.routes import perfumes
    from parfumier.types.routes import types
    from parfumier.reviews.routes import reviews
    from parfumier.main.routes import main
    from parfumier.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(perfumes)
    app.register_blueprint(types)
    app.register_blueprint(reviews)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
