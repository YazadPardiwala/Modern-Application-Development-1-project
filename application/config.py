import os

basedir = os.path.abspath(os.path.dirname(__file__))

desired_config = 'production'

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQL_ALCHEMY_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevConfig(Config):
    SQLITE_DB_DIR = basedir
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'db_directory\db.db')
    #print(SQLALCHEMY_DATABASE_URI)
    DEBUG = True

class ProdConfig(Config):
    SQLITE_DB_DIR = basedir
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'db_directory\db.db')
    #print(SQLALCHEMY_DATABASE_URI)
    DEBUG = False