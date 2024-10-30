from datetime import datetime, timezone
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import EditProfileForm, LoginForm, RegistrationForm

from app.models import User


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        # when you reference current_user, Flask-Login will invoke the user
        # loader callback function, which will run a database query that will
        # put the target user in the database session.
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():

    # Checks if the user is already logged-in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # Check if form is submitted with data and passes the validations
    if form.validate_on_submit():

        # Executes the query and returns a single scalar value
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        # Checks if user exists and password is correct
        if (user is None) or (not user.check_password(form.password.data)):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        # Registers the user as logged in
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')

        # netloc is the network location (e.g., example.com, localhost:8000),
        # if netloc is not empty it means url contains domain
        # Full url including the domain name is ignored due to the security
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    # Shows login page
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You are now registered")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(
        User.username == username))
    posts = [
        {"author": user, "body": "post 1"},
        {"author": user, "body": "post 2"}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route("/user/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Construct the form object
    form = EditProfileForm()
    # Check if it is post request
    if form.validate_on_submit():
        # Update the db
        if form.username.data != '':
            current_user.username = form.username.data
        if form.about_me.data != '':
            current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes are made")
    # return pre-filled form
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)
