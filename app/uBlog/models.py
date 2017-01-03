from sqlalchemy_utils import PasswordType
from sqlalchemy_utils import EmailType
from sqlalchemy_utils import force_auto_coercion
from sqlalchemy.sql.expression import text
from wtforms.validators import Regexp
from datetime import datetime

from uBlog import db

force_auto_coercion()

# class Config(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.JSON, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.now(), server_default=text('NOW()'))
    email = db.Column(EmailType(), index=True, unique=True)
    active = db.Column(db.Boolean, default=False, server_default=text('FALSE'))
    bio = db.Column(db.Text, nullable=False, default='', server_default='')
    bio_html = db.Column(db.Text)
    emojis = db.Column(db.Boolean, nullable=False, default=True, server_default=text('TRUE'))
    show_email = db.Column(db.Boolean, nullable=False, default=False, server_default=text('FALSE'))
    brewer = db.Column(db.Boolean, nullable=False, default=False, server_default=text('FALSE'))
    admin = db.Column(db.Boolean, nullable=False, default=False, server_default=text('FALSE'))
    json = db.Column(db.JSON, nullable=False, default=lambda: {})

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    beers = db.relationship('Beer', backref='brewer', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.id


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True, info={'validators': Regexp(r'^\w+$')})
    content = db.Column(db.Text, nullable=False, default='', server_default='')
    content_html = db.Column(db.Text)
    title = db.Column(db.String, nullable=False)
    menu_left = db.Column(db.Boolean, nullable=False, default=False, server_default=text('FALSE'))
    menu_right = db.Column(db.Boolean, nullable=False, default=False, server_default=text('FALSE'))

    # posts = db.relationship('Post', backref='page', lazy='dynamic')

    def __repr__(self):
        return '<Page %r>' % self.id


class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    content = db.Column(db.Text, nullable=False, default='')
    content_html = db.Column(db.Text)
    published = db.Column(db.DateTime, server_default=text('NOW()'))
    last_edit = db.Column(db.DateTime, server_default=text('NOW()'))
    listed = db.Column(db.Boolean, nullable=False, default=True, server_default=text('TRUE'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    posts = db.relationship('Post', backref='beer', lazy='dynamic')

    def last_update(self):
        dates = [post.last_edit for post in self.posts]
        dates.append(self.last_edit)
        return min(dates)

    def __repr__(self):
        return '<Beer %r>' % self.id


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    published = db.Column(db.DateTime, server_default=text('NOW()'))
    last_edit = db.Column(db.DateTime, server_default=text('NOW()'))

    beer_id = db.Column(db.Integer, db.ForeignKey('beer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, beer):
        self.beer_id = beer.id

    def __repr__(self):
        return '<Post %r %r>' % (self.beer_id, self.id)
