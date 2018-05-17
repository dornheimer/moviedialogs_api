import os
from dotenv import load_dotenv

API_BASE_PATH = '/api'
load_dotenv('.env')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
    ELASTICSEARCH_SETTINGS = '/home/iiu/python/populate_db/db/mapping.json'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite://')  # Use SQLite as fallback
    ELASTICSEARCH_URL = None
