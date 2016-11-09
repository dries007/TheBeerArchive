from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import FileField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms_alchemy import ModelForm
from wtforms_alchemy.validators import Unique
from wtforms.validators import Email

from app import app

from models import User
from models import Page
from models import Post


class LoginForm(Form):
    email = EmailField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    login = SubmitField('Log in')


class EditForm(Form):
    title = StringField('title', validators=[DataRequired()])
    editor = TextAreaField('editor', validators=[DataRequired()])
    save = SubmitField('Save')

