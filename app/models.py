from app import db
from app import bcrypt


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String, index=True, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, index=True, unique=True)
    bio = db.Column(db.String, default="", nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.password = bcrypt.generate_password_hash(password)

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
        return '<User %r>' % self.nickname


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    content = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)

    posts = db.relationship('Post', backref='page', lazy='dynamic')

    def __repr__(self):
        return '<Page %r>' % self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clazz = db.Column(db.String)
    content = db.Column(db.String, nullable=False)
    published = db.Column(db.DateTime)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.id
