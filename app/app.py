from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_gravatar import Gravatar
from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

import mimetypes
import os

mimetypes.init()
app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

#app.config.from_object(__name__ + '.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])
app.secret_key = os.environ['FLASK_SECRET']

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

lm = LoginManager(app)
lm.login_view = '/login'
gravatar = Gravatar(app, size=100, rating='g', default='mm', use_ssl=True)

##################################################################
from sqlalchemy_utils import PasswordType
from sqlalchemy_utils import EmailType
from sqlalchemy_utils import force_auto_coercion

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
    bio = db.Column(db.String, default="", nullable=False)
    bio_html = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # def __init__(self, nickname, email, password):
    #     self.name = nickname
    #     self.email = email
    #     self.password = password

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

##################################################################
from flask import Markup
from flask import request
from flask import escape
from flask_login import current_user

from lxml.html import clean
from mdx_gfm import GithubFlavoredMarkdownExtension
import markdown


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.context_processor
def context_processor():
    return dict(user=current_user, config=Config.query.get(0).data)


@app.template_filter('date')
def filter_date(datetime):
    return None if datetime is None else datetime.strftime('%-d %b %Y')


@app.template_filter('nl2br')
def filter_nl2br(text):
    return None if text is None else Markup('<br/>\n'.join(escape(text).splitlines()))


class SimpleTextReplacePattern(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern, replacement):
        super().__init__(pattern)
        self.replacement = '%s%s;' % (markdown.util.AMP_SUBSTITUTE, replacement)

    def handleMatch(self, m):
        return self.replacement


class HTMLEntitiesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('copy', SimpleTextReplacePattern(r'\([cC]\)', 'copy'), '_end')
        md.inlinePatterns.add('reg', SimpleTextReplacePattern(r'\([rR]\)', 'reg'), '_end')
        md.inlinePatterns.add('phonogram_rights', SimpleTextReplacePattern(r'\([pP]\)', '#x2117'), '_end')
        md.inlinePatterns.add('trademark', SimpleTextReplacePattern(r'\([Tt][Mm]\)', 'trade'), '_end')
        md.inlinePatterns.add('plus_minus', SimpleTextReplacePattern(r'\+-', 'plusmn'), '_end')


def make_markdown(text):
    if text is None or text == '':
        return '<div class="md"></div>'
    md = markdown.markdown(text, extensions=[GithubFlavoredMarkdownExtension(), HTMLEntitiesExtension()])
    cleaner = clean.Cleaner(links=False, add_nofollow=True)
    return '<div class="md">%s</div>' % cleaner.clean_html(md)


@app.template_filter('markdown')
def filter_markdown(text):
    return Markup(make_markdown(text))


def _test_menu_condition(condition):
    if condition['name'] == 'isurl':
        return condition.get('inverted', False) != (condition['data'] == request.path)
    elif condition['name'] == 'inurl':
        return condition.get('inverted', False) != (condition['data'] in request.path)
    elif condition['name'] == 'authenticated':
        return condition.get('inverted', False) != current_user.is_authenticated
    elif condition['name'] == 'active':
        return condition.get('inverted', False) != current_user.is_active
    elif condition['name'] == 'anonymous':
        return condition.get('inverted', False) != current_user.is_anonymous
    else:
        raise Exception('Condition unknown.', condition)
    pass


@app.template_test('menu_conditions')
def test_menu_conditions(item):
    if type(item) is str or 'conditions' not in item:
        return True
    return all(map(_test_menu_condition, item['conditions']))


##################################################################
from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import FileField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired
from wtforms.validators import Regexp
from wtforms.validators import Optional
from wtforms.validators import EqualTo
from wtforms.validators import Length
# from wtforms_alchemy import ModelForm
from wtforms_alchemy import model_form_factory
from wtforms_alchemy.validators import Unique
from wtforms.validators import Email

import re


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session


class ProfileForm(ModelForm):
    login = SubmitField('Log in')

    class Meta:
        model = User


class RegisterForm(ModelForm):
    register = SubmitField('Register')

    class Meta:
        model = User
        only = ['name', 'email', 'password']


class LoginForm(ModelForm):
    email = EmailField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6)])
    login = SubmitField('Log in')

# editor = TextAreaField('editor', validators=[Optional()])
# title = StringField('title', validators=[InputRequired(), Unique(Page.title)])
# name = StringField('name', validators=[InputRequired(), Regexp("^\w+$", re.IGNORECASE, message="Must be alphanumerical and underscores only.")])


class PageEditForm(ModelForm):
    save = SubmitField('Save')

    class Meta:
        mode = Page
        only = ['name', 'title', 'content']


# todo: enforce uniqe email / name & do email checking
class ProfileEditForm(ModelForm):
    email = EmailField('email', validators=[InputRequired(), Email(), Unique(User.name)])
    name = StringField('name', validators=[InputRequired(), Unique(User.name)])


# Must be after init & config, to avoid circular dependencies
# Will show up as unused


##################################################################
from flask import render_template
from flask import abort
from flask import redirect
from flask import request
from flask import flash

from flask_login import current_user
from flask_login import logout_user
from flask_login import login_user
from flask_login import login_required

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound


@app.errorhandler(HTTPException)
def any_error(e):
    return render_template('error.html', e=e), e.code


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or '/profile')
    form = LoginForm()
    if form.login.data and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).limit(1).first()
        if user:
            if user.password == form.password.data:
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash('Logged in!', 'success')
                return redirect(request.args.get('next') or '/profile')
        flash('Login details incorrect.', 'danger')
    return render_template('login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.register.data and form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('You still need to verify your email address before your account will be activated.', 'warning')

        # user = User.query.filter_by(email=form.email.data).limit(1).first()
        # if user:
        #     if user.password == form.password.data:
        #         db.session.add(user)
        #         db.session.commit()
        #         login_user(user, remember=True)
        #         return redirect(request.args.get('next') or '/profile')
        # flash('Login details incorrect.', 'danger')
    return render_template('register.html', form=form)


@app.route("/logout")
def logout():
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(request.args.get('next') or '/')


@app.route("/profile/<int:id>")
def profile(id):
    user = User.query.get(id)
    if user is None:
        raise NotFound("User %d not found." % id)
    return render_template('profile.html', profile=user)


@app.route("/profile")
@login_required
def own_profile():
    return render_template('profile.html', profile=current_user)


@app.route("/")
def index():
    page = Page.query.get(0)
    if page is None:
        raise NotFound('No index page!\nThe index page always has page id 0.')
    return render_template('page.html', page=page)


@app.route("/<name>")
def any_page(name):
    page = Page.query.filter_by(name=name).first()
    if page is None:
        raise NotFound('Page %s not found.' % name)
    return render_template('page.html', page=page)


# todo: authentication!!
@app.route("/edit/page/<int:id>", methods=['GET', 'POST'])
@app.route("/edit/page/", methods=['GET', 'POST'])
@login_required
def page_edit(id=0):
    page = Page.query.get(id)
    if page is None:
        page = Page()
    # form = PageEditForm(obj=page)
    # raise NotFound('This page does not exist.')
    form = PageEditForm(title=page.title, name=page.name, editor=page.content)

    if form.save.data and form.validate_on_submit():
        form.populate_obj(page)
        # page.title = form.title.data
        # page.name = form.name.data
        # page.content = form.editor.data
        page.content_html = make_markdown(page.content)
        db.session.add(page)
        db.session.commit()
        if id == 0:
            redirect('/edit/page/%d' % id)
    return render_template('edit_page.html', form=form, title=page.title, uniqueid="page-%d" % id)


@app.route("/edit/profile", methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = ProfileEditForm(editor=current_user.bio, email=current_user.email, name=current_user.name)
    if form.save.data and form.validate_on_submit():
        current_user.name = form.name.data
        current_user.bio = form.editor.data
        current_user.bio_html = '<p class="text-muted">This user has no bio set.</p>' if current_user.bio is None or current_user.bio == '' else make_markdown(current_user.bio)
        db.session.add(current_user)
        db.session.commit()
    return render_template('edit_profile.html', form=form, uniqueid="user-%d" % current_user.id)


##################################################################

# fixme: It's impossible to catch HTTPException. Flask Bug #941 (https://github.com/pallets/flask/issues/941)
from werkzeug.exceptions import default_exceptions
for code, ex in default_exceptions.items():
    app.errorhandler(code)(any_error)

if __name__ == '__main__':
    manager.run()
