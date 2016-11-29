from sqlalchemy_utils import PasswordType
from sqlalchemy_utils import EmailType
from sqlalchemy_utils import force_auto_coercion
from app import db

force_auto_coercion()


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    email = db.Column(EmailType(), index=True, unique=True)
    bio = db.Column(db.String, default="", nullable=False)
    bio_html = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, nickname, email, password):
        self.name = nickname
        self.email = email
        self.password = password

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.name


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    content = db.Column(db.String, nullable=False)
    content_html = db.Column(db.String)
    title = db.Column(db.String, nullable=False)

    posts = db.relationship('Post', backref='page', lazy='dynamic')

    def __repr__(self):
        return '<Page %r>' % self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clazz = db.Column(db.String)
    content = db.Column(db.String, nullable=False)
    content_html = db.Column(db.String)
    published = db.Column(db.DateTime)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.id
