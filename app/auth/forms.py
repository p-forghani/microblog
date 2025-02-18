from flask import current_app
import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db
from app.models import User


#  In WTForms custom validators, the function must accept both form and field
# as arguments, even if form is not used.
# a field passes validation if the custom validator function does not raise a
# ValidationError
def validate_password(form, field):
    if len(field.data) < current_app.config['MIN_PASSWORD_LENGTH']:
        raise ValidationError(
            f"Password must be at least "
            f"{current_app.config['MIN_PASSWORD_LENGTH']} characters long")
    # Uncomment this line if you want passwords contain letter
    # if not re.search(r"[A-Za-z]", field.data):
    #     raise ValidationError(
    #         "Password must contain as least 1 letter"
    #     )


# Define LoginForm class inheriting from FlaskForm
class LoginForm(FlaskForm):
    # Username field with DataRequired validator
    username = StringField('Username', validators=[DataRequired()])
    # Password field with DataRequired validator
    password = PasswordField('Password', validators=[DataRequired()])
    # Remember me checkbox
    remember_me = BooleanField('Remember Me')
    # Submit button
    submit = SubmitField('Sign In')


# Define RegistrationForm class inheriting from FlaskForm
class RegistrationForm(FlaskForm):
    # Username field with DataRequired validator
    username = StringField('Username', validators=[DataRequired()])
    # Email field with DataRequired and Email validators
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password field with DataRequired validator
    password = PasswordField('Password',
                             validators=[DataRequired(), validate_password])
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


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(), validate_password])
    new_password_2 = PasswordField(
        'Repeat New Password',
        validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')
