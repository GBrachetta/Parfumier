import os


class Config(object):
    '''
    EXPLANATION
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    DEBUG = True
    