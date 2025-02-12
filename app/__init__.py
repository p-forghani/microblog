import logging
from flask_babel import Babel
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)


def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


login = LoginManager(app)
login.login_view = 'login'

app.config.from_object(Config)

db = SQLAlchemy(app)

mail = Mail(app)

migrate = Migrate(app, db)

moment = Moment(app)

# The Babel instance is created and initialized with the Flask app
# The locale_selector argument is a function that is called to choose
# the language to use for the request
# The best_match method of the request.accept_languages object returns the
# best language for the client to use based on the Accept-Language header sent
# by the client

# I did not use the bable in this project but initiated it only for future
# updates.
babel = Babel(app, locale_selector=get_locale)

if (not app.debug):
    # Config the log file
    if not os.path.exists('logs'):
        os.mkdir("logs")
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Microblog Startup")

# The bottom import is a well known workaround that avoids circular imports
# We need to import app variable in the routes.py
from app import errors, models, routes  # noqa
