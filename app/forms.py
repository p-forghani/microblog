# Import necessary modules and packages
import sqlalchemy as sa
import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms.validators import Length

# Import application and database instances
from app import db, app
# Import User model
from app.models import User


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
        if len(password.data) < app.config['MIN_PASSWORD_LENGTH']:
            raise ValidationError(
                f"Password must be at least "
                f"{app.config['MIN_PASSWORD_LENGTH']} characters long")
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

    def __init__(self, current_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_username = current_username

    def validate_username(self, username):
        # If username == current user. pass
        # if username is unique. pass
        # if username is duplicate: raise
        if username.data != self.current_username:
            user = db.session.scalar(
                sa.select(User).where(username.data == User.username)
            )
            if user is not None:
                raise ValidationError("Such username already exists.")


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say Something', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password_2 = PasswordField(
        'Repeat New Password',
        validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')
