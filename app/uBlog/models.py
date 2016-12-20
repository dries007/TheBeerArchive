from sqlalchemy_utils import PasswordType
from sqlalchemy_utils import EmailType
from sqlalchemy_utils import force_auto_coercion

from uBlog import db

force_auto_coercion()


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    email = db.Column(EmailType(), index=True, unique=True)
    active = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, nullable=False, default='')
    bio_html = db.Column(db.Text)
    emojis = db.Column(db.Boolean, nullable=False, default=True)
    showEmail = db.Column(db.Boolean, nullable=False, default=False)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

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
        return '<User %r>' % self.id


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    content = db.Column(db.Text, nullable=False, default='')
    content_html = db.Column(db.Text)
    title = db.Column(db.String, nullable=False)

    posts = db.relationship('Post', backref='page', lazy='dynamic')

    def __repr__(self):
        return '<Page %r>' % self.id


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    published = db.Column(db.DateTime)
    last_edit = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, page):
        self.page_id = page.id

    def __repr__(self):
        return '<Post %r %r>' % (self.page_id, self.id)
