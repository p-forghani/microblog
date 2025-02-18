import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config


login = LoginManager()
login.login_view = 'auth.login'
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)

    # Middle import to avoid circular dependencies
    from app.errors import bp as errors_bp  # noqa
    from app.auth import bp as auth_bp  # noqa
    from app.main import bp as main_bp  # noqa
    app.register_blueprint(errors_bp)
    app.register_blueprint(blueprint=auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    if (not app.debug) and (not app.testing):
        # Config the log file
        if not os.path.exists('logs'):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            'logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s "
            "[in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Microblog Startup")

    return app

# The bottom import is a well known workaround that avoids circular imports
# We need to import app variable in the routes.py
from app import models  # noqa
