from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import (LoginForm, RegistrationForm, ResetPasswordForm,
                            ResetPasswordRequestForm)
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():

    # Checks if the user is already logged-in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

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
            return redirect(url_for('auth.login'))

        # Registers the user as logged in
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')

        # netloc is the network location (e.g., example.com, localhost:8000),
        # if netloc is not empty it means url contains domain
        # Full url including the domain name is ignored due to the security
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    # Shows login page
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You are now registered")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route("/reset_password_request", methods=['POST', 'GET'])
def reset_password_request():
    form = ResetPasswordRequestForm()

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        # Check if email exists in db.
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)
        flash("If your email is correct, the instructions to change "
              "your password is sent to your email.")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        print('good to go')
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password has been changed succussfully.")
        return redirect(url_for('auth.login'))
    print('not good to go')
    return render_template('auth/reset_password.html', title='Reset Password',
                           form=form)
