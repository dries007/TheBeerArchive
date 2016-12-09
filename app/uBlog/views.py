from flask import render_template
from flask import redirect
from flask import request
from flask import flash

from flask_login import current_user
from flask_login import logout_user
from flask_login import login_user
from flask_login import login_required

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound

from uBlog import db, app
from uBlog.models import User, Page
from uBlog.forms import LoginForm, RegisterForm, PageEditForm, ProfileEditForm
from uBlog.helpers import make_markdown


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
