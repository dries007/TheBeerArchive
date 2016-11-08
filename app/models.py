from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
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
