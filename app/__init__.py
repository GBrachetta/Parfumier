from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'
app.config['MONGO_URI'] = Config.MONGO_URI
mongo = PyMongo(app)

from app import routes, users 