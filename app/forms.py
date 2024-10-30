import sqlalchemy as sa
import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms.validators import Length

from app import db
from app.models import User
from app.constants import MIN_PASSWORD_LENGTH


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    # When you add any methods that match the pattern validate_<field_name>,
    # WTForms takes those as custom validators and invokes them in addition
    # to the stock validators.
    def validate_username(self, username):
        user = db.session.scalar(
            sa.select(User).where(User.username == username.data)
        )
        if user is not None:
            raise ValidationError("Username already exists")

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data)
        )
        if user is not None:
            raise ValidationError("Email already exists")

    def validate_password(self, password):
        if len(password.data) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f"Password must be at least \
                                  {MIN_PASSWORD_LENGTH} characters long")
        if not re.search(r"[A-Za-z]", password.data):
            raise ValidationError(
                "Password must contain as least 1 letter"
            )


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField("About Me", validators=[
        Length(0, 140),
    ])
    submit = SubmitField('Submit')
