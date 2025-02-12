import hashlib
from datetime import datetime, timezone
from time import time
from typing import Optional

import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db, login

followers = sa.Table(
    "followers",
    db.metadata,
    # Marking both columns as primary key is called compound primary key
    sa.Column('follower_id', sa.Integer, sa.ForeignKey(column='user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)


class User(UserMixin, db.Model):

    # Flask-SQLAlchemy uses a "snake case" naming convention for database
    # tables by default. If you prefer to choose your own table names,
    # you can add an attribute named __tablename__ to the model class.
    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))

    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(

        default=lambda: datetime.now(timezone.utc)
    )

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )

    followings: so.WriteOnlyMapped['User'] = so.relationship(
        secondary='followers',
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary='followers',  # it is the name of the association table
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='followings'

    )

    def __repr__(self):

        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        email_hash = hashlib.md5(
            self.email.lower().strip().encode()
        ).hexdigest()
        avatar_url = (
            f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=mp")
        return avatar_url

    def follow(self, user):
        if not self.is_following(user):
            self.followings.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followings.remove(user)

    def is_following(self, user):
        # All write-only relationships have a select() method that constructs
        # a query that returns all the elements in the relationship.
        q = self.followings.select().where(User.id == user.id)
        return db.session.scalar(q) is not None

    def followers_count(self):
        q = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(q)

    def following_count(self):
        q = sa.select(sa.func.count()).select_from(
            self.followings.select().subquery()
        )
        return db.session.scalar(q)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            key=app.config['SECRET_KEY'],
            algorithm='HS256',
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, key=app.config['SECRET_KEY'],
                            algorithms='HS256')['reset_password']
        except Exception:
            return
        return db.session.get(User, id)

    def following_posts(self):
        """Returns posts made by users that the current user ('self') follows,
        as well as the current user's own posts."""

        # Creating aliased versions of the User model:
        # - `Author`: Represents the users who are authors of posts.
        # - `Follower`: Represents the users who follow those authors
        # (including 'self').
        # Using aliases allows us to reference `User` in multiple roles within
        # the query.
        Author = so.aliased(User)
        Follower = so.aliased(User)

        return (
            # Start building the SQLAlchemy query by selecting all `Post`
            # entries.
            sa.select(Post)

            # Join `Post.author` (i.e., the user who wrote the post) to our
            # alias `Author`.
            # `.of_type(Author)` specifies that we want to reference the `User`
            # model as `Author`.
            .join(Post.author.of_type(Author))

            # Perform an outer join between the `Author`'s followers and the
            # alias `Follower`.
            # This join retrieves all followers of each `Author`, including
            # "self" if they are a follower.
            # `isouter=True` indicates a left outer join, so posts are still
            # included if `Author` has no followers.
            .join(Author.followers.of_type(Follower), isouter=True)

            # Filter to only include posts where:
            # - The current user (`self`) is either the `Follower` (i.e., they
            # follow the `Author`), or
            # - The current user (`self`) is the `Author` (to include their
            # own posts).
            .where(sa.or_(
                self.id == Follower.id,  # self is following the author
                self.id == Author.id     # self is the author
            ))

            # Group results by each post. This ensures that each post only
            # appears once.
            .group_by(Post)

            # Order the posts by time_stamp in descending order (newest first).
            .order_by(Post.time_stamp.desc())
        )


class Post(db.Model):
    __tablename__ = 'post'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    time_stamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(tz=timezone.utc)
    )

    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    # Add index=True since Not all databases automatically create an index for
    # foreign keys.
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return f"<Post {self.body}"


# When you reference current_user, Flask-Login will invoke the user loader
# callback function
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
