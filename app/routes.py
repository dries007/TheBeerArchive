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

from app import bcrypt
from app import app
from app import db

from models import User
from models import Page
from models import Post

from forms import LoginForm
from forms import EditForm
from forms import PageEditForm


@app.errorhandler(HTTPException)
def any_error(e):
    return render_template('error.html', e=e), e.code


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.login.data and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).limit(1).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(request.args.get('next') or '/profile')
        flash('Login details incorrect.', 'danger')
    return render_template('login.html', form=form)


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


@app.route("/edit/page/<int:id>", methods=['GET', 'POST'])
def page_edit(id):
    page = Page.query.get(id)
    if page is None:
        raise NotFound('This page does not exist.')
    form = PageEditForm(title=page.title, name=page.name, editor=page.content)
    if form.save.data and form.validate_on_submit():
        page.title = form.title.data
        page.name = form.name.data
        page.content = form.editor.data
        db.session.add(page)
        db.session.commit()
    return render_template('edit.html', form=form, title=page.title, uniqueid="page-%d" % id)
