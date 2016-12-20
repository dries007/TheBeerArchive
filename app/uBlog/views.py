import datetime
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
from uBlog.models import User, Page, Post
from uBlog.forms import LoginForm, RegisterForm, PageEditForm, ProfileEditForm, PostEditForm
from uBlog.helpers import make_markdown


# todo: authentication!!


@app.errorhandler(HTTPException)
def any_error(e):
    return render_template('error.html', e=e), e.code


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


@app.route("/logout")
def logout():
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(request.args.get('next') or '/')


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
        return redirect(request.args.get('next') or '/profile')
    return render_template('register.html', form=form)


@app.route("/profile")
@login_required
def own_profile():
    return render_template('profile.html', profile=current_user, own_profile=True)


@app.route("/edit/profile", methods=['GET', 'POST'])
@login_required
def profile_edit():
    user = User.query.get(current_user.id)
    form = ProfileEditForm(obj=user)
    if form.save.data and form.validate_on_submit():
        form.populate_obj(user)
        user.bio_html = make_markdown(user.bio, empty='<p class="text-muted">This user has no bio set.</p>', clazz="md md-profile")
        db.session.add(user)
        db.session.commit()
    return render_template('edit_profile.html', form=form, uniqueid="user-%d" % user.id)


@app.route("/profile/<int:id>")
def profile(id):
    user = User.query.get(id)
    if user is None:
        raise NotFound("User %d not found." % id)
    return render_template('profile.html', profile=user, own_profile=False)


@app.route("/edit/page/<int:page_id>", methods=['GET', 'POST'])
@app.route("/edit/page/", methods=['GET', 'POST'])
@login_required
def page_edit(page_id=-1):
    if page_id == -1:
        page = Page()
    else:
        page = Page.query.get(page_id)
        if page is None:
            raise NotFound('Page %s not found.' % page_id)

    form = PageEditForm(obj=page)

    if form.save.data and form.validate_on_submit():
        form.populate_obj(page)
        page.content_html = make_markdown(page.content, clazz="md md-page")
        db.session.add(page)
        db.session.commit()
        if page_id == -1:
            return redirect('/edit/page/%d' % page_id)
    return render_template('edit_page.html', form=form, title=page.title, uniqueid="page-%d" % page_id)


@app.route("/edit/post/<int:post_id>", methods=['GET', 'POST'])
@app.route("/edit/post", methods=['GET', 'POST'])
@login_required
def post_edit(post_id=-1):
    if post_id == -1:
        page_id = int(request.args.get('page'))
        page = Page.query.get(page_id)
        if page is None:
            raise NotFound('Page %d not found.' % page_id)
        post = Post(page)
    else:
        post = Post.query.get(post_id)
        if post is None:
            raise NotFound('Post %d not found.' % post_id)

    form = PostEditForm(obj=post)
    if form.save.data and form.validate_on_submit():
        form.populate_obj(post)
        if post.published is None:
            post.published = datetime.datetime.utcnow()
        post.user_id = current_user.id
        post.last_edit = datetime.datetime.utcnow()
        post.content_html = make_markdown(post.content, clazz="md md-page")
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
        post_id = post.id
        if post_id == -1:
            return redirect('/edit/post/%d' % post_id)
    return render_template('edit_post.html', form=form, new=post_id == -1, uniqueid="post-%d" % post_id, post=post)


@app.route("/del/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get(post_id)
    if post is None:
        raise NotFound('Post %d not found.' % post_id)
    post.active = False
    db.session.delete(post)
    db.session.commit()
    return redirect('/%s' % post.page.name)
