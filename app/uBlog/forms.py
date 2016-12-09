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

from uBlog import db
from uBlog.models import User, Page

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
