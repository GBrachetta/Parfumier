"""sumary_line"""
import os


class Config:
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")
    MONGO_URI = os.environ.get("MONGO_URI")
