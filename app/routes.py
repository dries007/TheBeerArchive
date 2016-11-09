from flask import render_template
from flask import abort
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound

from app import app
from app import db

from models import User
from models import Page
from models import Post

from forms import LoginForm
from forms import EditForm


@app.errorhandler(HTTPException)
def any_error(e):
    return render_template('error.html', e=e), e.code


@app.route("/login")
def login():
    return ""


@app.route("/edit/page/<int:id>", methods=['GET', 'POST'])
def page_edit(id):
    page = Page.query.get(id)
    if page is None:
        raise NotFound('This page does not exist.')
    form = EditForm(title=page.title, editor=page.content)
    if form.save.data and form.validate_on_submit():
        page.title = form.title.data
        page.content = form.editor.data
        db.session.add(page)
        db.session.commit()

    return render_template('edit.html', form=form, title=page.title, uniqueid="page-%d" % id)


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
        abort(404)
    return render_template('page.html', page=page)


