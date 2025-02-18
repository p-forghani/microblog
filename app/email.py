# Next 2 imports are for SendGrid which is disabled for now
# from app import sg
# from sendgrid.helpers.mail import Mail

from app import mail
from flask import current_app
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
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
        ).start()

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
