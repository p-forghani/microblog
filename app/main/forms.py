# Import necessary modules and packages
import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

# Import application and database instances
from app import db
# Import User model
from app.models import User


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
