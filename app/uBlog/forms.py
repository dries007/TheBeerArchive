from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, Email
from wtforms_alchemy import model_form_factory

from uBlog import db
from uBlog.models import User, Page, Post


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
        model = Page
        only = ['name', 'title', 'content']


class ProfileEditForm(ModelForm):
    save = SubmitField('Save')

    class Meta:
        model = User
        only = ['name', 'email', 'bio', 'emojis']


class PostEditForm(ModelForm):
    save = SubmitField('Save')

    class Meta:
        model = Post
        only = ['content']
