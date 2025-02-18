from app.models import User
from app.email import send_email
from flask import render_template, current_app


def send_password_reset_email(user: User):
    token = user.get_reset_password_token()
    send_email(
        subject="Reset Your Password",
        recipients=[user.email],
        sender=current_app.config['ADMINS'][0],
        text_body=render_template('auth/email/reset_password.txt', user=user,
                                  token=token),
        html_body=render_template('auth/email/reset_password.html', user=user,
                                  token=token),
    )
