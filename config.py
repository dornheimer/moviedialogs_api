import os
from dotenv import load_dotenv

APP_DIR = os.path.abspath(os.path.dirname(__file__))
API_BASE_PATH ='/api'
load_dotenv(os.path.join(APP_DIR, '.env'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database
