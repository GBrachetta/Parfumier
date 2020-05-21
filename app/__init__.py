from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = "usersBP.login"
login_manager.login_message = "Please log in."
login_manager.login_message_category = "info"
app.config["MONGO_URI"] = Config.MONGO_URI
mongo = PyMongo(app)

"""
Imports bellow need to happen after initialisation of the app
to prevent circular imports.
"""

from app import models

from app.usersBP.routes import usersBP
from app.perfumesBP.routes import perfumesBP
from app.typesBP.routes import typesBP
from app.reviewsBP.routes import reviewsBP
from app.main.routes import main

app.register_blueprint(usersBP)
app.register_blueprint(perfumesBP)
app.register_blueprint(typesBP)
app.register_blueprint(reviewsBP)
app.register_blueprint(main)
