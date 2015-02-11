import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True

    #-------- ORIENTDB Config ----------
    ORIENTDB_SERVER_URL = 'http://localhost'
    ORIENTDB_SERVER_PORT = '5551'
    ORIENTDB_USER = 'root'
    ORIENTDB_PASSWORD = 'parola123'
    ORIENTDB_DB_NAME = 'FaceBook_Scrapper'

    #------- ELASTICSERCH Config ----------
    ES_SERVER_URL = 'http://localhost'
    ES_SERVER_PORT = '5552'


