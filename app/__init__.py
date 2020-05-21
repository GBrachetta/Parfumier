from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = "users.login"
login_manager.login_message = "Please log in."
login_manager.login_message_category = "info"
mongo = PyMongo(app)

"""
Imports bellow need to happen after initialisation of the app
to prevent circular imports.
"""

from app import models
from app.users.routes import users
from app.perfumes.routes import perfumes
from app.types.routes import types
from app.reviews.routes import reviews
from app.main.routes import main

app.register_blueprint(users)
app.register_blueprint(perfumes)
app.register_blueprint(types)
app.register_blueprint(reviews)
app.register_blueprint(main)
