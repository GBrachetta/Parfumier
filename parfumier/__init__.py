"""
Imports the primordial elements to be initialised:
LoginManager deals with the user in session
PyMongo is the connection to the database
Config is the class reading the enviroment variables
Compress permits to use gzip to allow text compression
and accelerate the loading times.
"""
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from parfumier.config import Config
from flask_compress import Compress

"""Instantiates and configures app

Defines login_manager, the mongodb connector
and the Compress class allowing faster delivery of text gzipped.
"""

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Please log in."
login_manager.login_message_category = "info"
mongo = PyMongo()
compress = Compress()


def create_app(config_class=Config):
    """Creates the app

    Initialises the app and all the required components.
    Compresses the text delivery.
    Imports and registers all blueprints.
    Reads configuration from file with variables.
    Returns the initialised app.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    compress.init_app(app)
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
