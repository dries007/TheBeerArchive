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

from app import app
from app import db

from models import User
from models import Page
from models import Post

import re


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session


class LoginForm(ModelForm):
    login = SubmitField('Log in')

    class Meta:
        model = User
        only = ['email', 'password']

# class LoginForm(ModelForm):
#     email = EmailField('email', validators=[InputRequired(), Email()])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=6)])
#     login = SubmitField('Log in')


class EditForm(ModelForm):
    editor = TextAreaField('editor', validators=[Optional()])
    save = SubmitField('Save')


class PageEditForm(EditForm):
    title = StringField('title', validators=[InputRequired(), Unique(Page.title)])
    name = StringField('name', validators=[InputRequired(), Regexp("^\w+$", re.IGNORECASE, message="Must be alphanumerical and underscores only.")])


# todo: enforce uniqe email / name & do email checking
class ProfileEditForm(EditForm):
    email = EmailField('email', validators=[InputRequired(), Email(), Unique(User.name)])
    name = StringField('name', validators=[InputRequired(), Unique(User.name)])
