from flask import render_template

# Next 2 imports are for SendGrid which is disabled for now
# from app import sg
# from sendgrid.helpers.mail import Mail

from app import app, mail
from app.models import User
from flask_mail import Message
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, sender, html_body, text_body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=sender,
    )
    msg.html = html_body
    msg.body = text_body
    Thread(target=send_async_email, args=(app, msg)).start()

    # # This block is configuration is for SendGrid which is disabled for now
    # message = Mail(
    #     from_email=sender,
    #     to_emails=recipients,
    #     subject=subject,
    #     html_content=html_body,
    #     plain_text_content=text_body,
    # )
    # try:
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    # except Exception as e:
    #     print(e)


def send_password_reset_email(user: User):
    token = user.get_reset_password_token()
    send_email(
        subject="Reset Your Password",
        recipients=[user.email],
        sender=app.config['ADMINS'][0],
        text_body=render_template('email/reset_password.txt', user=user,
                                  token=token),
        html_body=render_template('/email/reset_password.html', user=user,
                                  token=token),
    )
