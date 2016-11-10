from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import FileField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.validators import Regexp
from wtforms.validators import Optional
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms_alchemy import ModelForm
from wtforms_alchemy.validators import Unique
from wtforms.validators import Email

from app import app

from models import User
from models import Page
from models import Post

import re


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    login = SubmitField('Log in')


class EditForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    editor = TextAreaField('editor', validators=[DataRequired()])
    save = SubmitField('Save')


class PageEditForm(EditForm):
    name = StringField('name', validators=[DataRequired(), Regexp("\w+", re.IGNORECASE)])


