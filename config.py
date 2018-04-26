import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', 'sqlite:///' + os.path.join(APP_DIR, 'movie_dialogs.sqlite')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
