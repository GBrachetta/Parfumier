# WORKING
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
app.config["MONGO_URI"] = Config.MONGO_URI
mongo = PyMongo(app)


from app.users.routes import users
from app.perfumes.routes import perfumes
from app.types.routes import types
from app.reviews.routes import reviews
from app.main.routes import main
from app.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(perfumes)
app.register_blueprint(types)
app.register_blueprint(reviews)
app.register_blueprint(main)
app.register_blueprint(errors)


# Want it working
# from flask import Flask
# from flask_login import LoginManager
# from flask_pymongo import PyMongo
# from app.config import Config


# login_manager = LoginManager()
# login_manager.login_view = "users.login"
# login_manager.login_message = "Please log in."
# login_manager.login_message_category = "info"
# mongo = PyMongo()


# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     login_manager.init_app(app)
#     mongo.init_app(app)
#     from app.users.routes import users
#     from app.perfumes.routes import perfumes
#     from app.types.routes import types
#     from app.reviews.routes import reviews
#     from app.main.routes import main
#     from app.errors.handlers import errors

#     app.register_blueprint(users)
#     app.register_blueprint(perfumes)
#     app.register_blueprint(types)
#     app.register_blueprint(reviews)
#     app.register_blueprint(main)
#     app.register_blueprint(errors)

#     return app
