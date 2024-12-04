import os
from pathlib import Path

basedir = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or \
        f'sqlite:///{basedir / "app.db"}'

    # Email server configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMINS = ['forghani.dev@gmail.com']

    MIN_PASSWORD_LENGTH = 4
    POSTS_PER_PAGE = 3
