from datetime import datetime, timezone
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.email import send_password_reset_email
from app.forms import (EditProfileForm, EmptyForm, LoginForm, PostForm,
                       RegistrationForm, ResetPasswordRequestForm,
                       ResetPasswordForm)
from app.models import User, Post


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        # when you reference current_user, Flask-Login will invoke the user
        # loader callback function, which will run a database query that will
        # put the target user in the database session.
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    # if it is a POST request
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is sent")
        # It is a standard practice to always respond to a POST request
        # generated by a web form submission with a redirect. This simple
        # trick is called the Post/Redirect/Get pattern. It avoids inserting
        # duplicate posts when a user inadvertently refreshes the page after
        # submitting a web form.
        return redirect(url_for('index'))
    # if it is a GET request
    # You may use the `posts` object with the all() to create a list
    # posts = db.session.scalars(current_user.following_posts())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        current_user.following_posts(), page=page,
        per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    # You can add any keyword arguments to <url_for()>, and if the names of
    # those arguments are not part of the URL that is defined for the route,
    # then Flask will include them as query arguments.
    if posts.has_next:
        next_url = url_for('index', page=posts.next_num)
    else:
        next_url = None
    # This implementation method is to recall your python skills.
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev \
        else None
    return render_template('index.html', title='Home', posts=posts.items,
                           form=form, prev_url=prev_url,
                           next_url=next_url)


@app.route('/explore')
@login_required
def explore():
    query = sa.select(Post).order_by(Post.time_stamp.desc())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        query, page=page, per_page=app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


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
    page = request.args.get('page', 1, type=int)
    # user.posts relationship is defined as a write-only relationship,
    # so the attribute has a select() method.
    query = user.posts.select().order_by(Post.time_stamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           form=form, next_url=next_url, prev_url=prev_url)


@app.route("/user/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Construct the form object
    form = EditProfileForm(current_user.username)
    # Check if it is post request
    if form.validate_on_submit():
        # Update the db
        if form.username.data != '':
            current_user.username = form.username.data
        if form.about_me.data != '':
            current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes are made")
        return redirect(url_for('edit_profile'))
    # return pre-filled form
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@app.route("/follow/<username>", methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f"Username {username} not found")
            return redirect(url_for('index'))
        if user == current_user:
            flash("You can not follow yourself")
            return redirect(url_for('index'))
        current_user.follow(user)
        db.session.commit()
        flash(f"You followed {username}")
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            User.username == username))
        if user is None:
            flash(f"Username {username} not found")
            return redirect(url_for('index'))
        if user == current_user:
            flash("You can not unfollow yourself")
            return redirect(url_for('index'))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are not following {username}")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route("/reset_password_request", methods=['POST', 'GET'])
def reset_password_request():
    form = ResetPasswordRequestForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        # Check if email exists in db.
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)
        flash("If your email is correct, the instructions to change "
              "your password is sent to your email.")
        return redirect(url_for('login'))

    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        print('good to go')
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password has been changed succussfully.")
        return redirect(url_for('login'))
    print('not good to go')
    return render_template('reset_password.html', title='Reset Password',
                           form=form)
