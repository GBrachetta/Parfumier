import os
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_mail import Mail
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in."
login_manager.login_message_category = "info"
app.config["MONGO_URI"] = Config.MONGO_URI
mongo = PyMongo(app)
app.config["MAIL_SERVER"] = "smtp.strato.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASS")
mail = Mail(app)

from app import routes, models
