# working
import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MONGO_URI = os.environ.get("MONGO_URI")


# Wnat this working
# import os


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY")
#     MONGO_URI = os.environ.get("MONGO_URI")
