from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model."""

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    posts = db.relationship('Feedback', backref='user',
                            cascade='all, delete-orphan')

    @classmethod
    def get_user(cls, username):
        """Return user data by username without password."""
        user = cls.query.get_or_404(username)
        del user.password
        return user

    @classmethod
    def register(cls, username, password, email_address, first_name, last_name):
        """Register new user."""

        hashed = bcrypt.generate_password_hash(password, rounds=14)
        hashed_utf = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf, email_address=email_address, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user."""

        user = User.query.filter_by(username=username).one_or_none()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Feedback(db.Model):
    """Feedback model."""

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'))

    # def serialize(self):
    #     """Serialized version of post data."""

    #     return {
    #         'title':self.title,
    #         'content':self.content,
    #         'username':self.username,
    #     }

    @classmethod
    def get_user_posts(cls, username):
        """Return all posts by a user."""

        return cls.query.filter_by(username=username).all()
