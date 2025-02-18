from flask import render_template

from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    # Default of the return code value is 200, in others cases,
    # the code should be returned.
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
