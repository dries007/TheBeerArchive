from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, Email
from wtforms_alchemy import model_form_factory

from uBlog import db
from uBlog.models import User, Page, Post, Beer


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session

# class ProfileForm(ModelForm):
#     login = SubmitField('Log in')
#
#     class Meta:
#         model = User


class RegisterForm(ModelForm):
    register = SubmitField('Register')

    class Meta:
        model = User
        only = ['name', 'email', 'password']


class PasswordResetRequestForm(ModelForm):
    email = EmailField('email', validators=[InputRequired(), Email()])
    request = SubmitField('Request reset link')


class PasswordResetForm(ModelForm):
    password = PasswordField('password', validators=[InputRequired(), Length(min=6)])
    confirm = SubmitField('Confirm')


class LoginForm(ModelForm):
    email = EmailField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6)])
    login = SubmitField('Log in')

# editor = TextAreaField('editor', validators=[Optional()])
# title = StringField('title', validators=[InputRequired(), Unique(Page.title)])
# name = StringField('name', validators=[InputRequired(), Regexp("^\w+$", re.IGNORECASE, message="Must be alphanumerical and underscores only.")])


class BeerEditForm(ModelForm):
    save = SubmitField('Save')
    delete = SubmitField('Delete')

    class Meta:
        model = Beer
        only = ['name', 'content', 'listed']


class PageEditForm(ModelForm):
    save = SubmitField('Save')
    delete = SubmitField('Delete')

    class Meta:
        model = Page
        only = ['name', 'title', 'content', 'menu_left', 'menu_right']


# todo: do email checking
class ProfileEditForm(ModelForm):
    save = SubmitField('Save')

    class Meta:
        model = User
        only = ['name', 'email', 'bio', 'emojis', 'show_email']


class PostEditForm(ModelForm):
    save = SubmitField('Save')
    delete = SubmitField('Delete')

    class Meta:
        model = Post
        only = ['content']
