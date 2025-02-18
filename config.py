import os
from pathlib import Path

from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or \
        f'sqlite:///{basedir / "app.db"}'

    ADMINS = ['forghani.dev@gmail.com']

    MIN_PASSWORD_LENGTH = 4
    POSTS_PER_PAGE = 10
    LANGUAGES = ['en', 'fa']
