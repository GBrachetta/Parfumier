"""Only os needed for the config file"""
import os


class Config:
    """Reads variables

    Reads the variables from my hidden file (locally)
    and my config variables (Heroku)
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")
    MONGO_URI = os.environ.get("MONGO_URI")
