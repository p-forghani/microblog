from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm
from app.models import User


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
