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
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden

from uBlog import db, app
from uBlog.models import User, Page, Post, Beer
from uBlog.forms import LoginForm, RegisterForm, PageEditForm, ProfileEditForm, PostEditForm, BeerEditForm
from uBlog.helpers import make_markdown, admin_required


@app.errorhandler(HTTPException)
def any_error(e):
    return render_template('error.html', e=e), e.code


@app.route("/")
def view_index():
    page = Page.query.get(1)
    if page is None:
        raise NotFound('No index page!\nThe index page always has page id 1.')
    return render_template('page.html', page=page)


@app.route("/<name>")
def view_any_page(name):
    page = Page.query.filter_by(name=name).first()
    if page is None:
        raise NotFound('Page %s not found.' % name)
    return render_template('page.html', page=page)


@app.route("/login", methods=['GET', 'POST'])
def view_login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or '/profile')
    form = LoginForm()
    if form.login.data and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).limit(1).first()
        if user:
            if not user.is_active:
                flash('Your account is not active.', 'danger')
                return render_template('login.html', form=form)
            if user.password == form.password.data:
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash('Logged in!', 'success')
                return redirect(request.args.get('next') or '/profile')
        flash('Login details incorrect.', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def view_logout():
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(request.args.get('next') or '/')


@app.route("/register", methods=['GET', 'POST'])
def view_register():
    form = RegisterForm()
    if form.register.data and form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # todo: Actually check email
        flash('You still need to verify your email address before your account will be activated.', 'warning')
        return redirect(request.args.get('next') or '/profile')
    return render_template('register.html', form=form)


@app.route("/beers")
@app.route("/beer")
def view_beers():
    return render_template('beers.html')


@app.route("/beer/<int:beer_id>")
def view_beer(beer_id):
    beer = Beer.query.get(beer_id)
    if beer is None:
        raise NotFound('Beer %s not found.' % beer_id)
    return render_template('beer.html', beer=beer)


@app.route("/edit/beer/<int:beer_id>", methods=['GET', 'POST'])
@app.route("/edit/beer/", methods=['GET', 'POST'])
@login_required
def view_beer_edit(beer_id=None):
    if beer_id is None:
        if not current_user.brewer:
            raise Forbidden('You are not allowed to make new beers.')
        beer = Beer()
    else:
        beer = Beer.query.get(beer_id)
        if beer is None:
            raise NotFound('Beer %s not found.' % beer_id)
        if current_user.id != beer.user_id and not current_user.admin:
            raise Forbidden('This is not your beer to edit.')

    form = BeerEditForm(obj=beer)

    if form.save.data and form.validate_on_submit():
        form.populate_obj(beer)
        if beer.published is None:
            beer.published = datetime.datetime.utcnow()
            beer.user_id = current_user.id
        beer.last_edit = datetime.datetime.utcnow()
        beer.content_html = make_markdown(beer.content, clazz="md md-page")
        db.session.add(beer)
        db.session.commit()
        db.session.refresh(beer)
        if beer_id is None:
            return redirect('/beer/%d' % beer.id)
    return render_template('edit_beer.html', form=form, title=beer.name, uniqueid="beer-%s" % beer_id)


@app.route("/profile")
@login_required
def view_own_profile():
    return render_template('profile.html', profile=current_user, own_profile=True)


@app.route("/edit/profile", methods=['GET', 'POST'])
@login_required
def view_profile_edit():
    user = User.query.get(current_user.id)
    form = ProfileEditForm(obj=user)
    if form.save.data and form.validate_on_submit():
        form.populate_obj(user)
        user.bio_html = make_markdown(user.bio, empty='<p class="text-muted">This user has no bio set.</p>', clazz="md md-profile")
        db.session.add(user)
        db.session.commit()
    return render_template('edit_profile.html', form=form, uniqueid="user-%s" % user.id)


@app.route("/profile/<user_id>")
def view_profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User %d not found." % user_id)
    return render_template('profile.html', profile=user, own_profile=False)


@app.route("/edit/post/<int:post_id>", methods=['GET', 'POST'])
@app.route("/edit/post", methods=['GET', 'POST'])
@login_required
def view_post_edit(post_id=None):
    if post_id is None:
        if not request.args.get('beer'):
            raise BadRequest('Missing beer data.')
        page_id = int(request.args.get('beer'))
        beer = Beer.query.get(page_id)
        if beer is None:
            raise NotFound('Beer %d not found.' % page_id)
        if beer.user_id != current_user.id and not current_user.admin:
            raise Forbidden('This is not your beer. You can\'t post to it.')
        post = Post(beer)
    else:
        post = Post.query.get(post_id)
        if post.user_id != current_user.id and not current_user.admin:
            raise Forbidden('This is not your post. You can\'t edit it.')
        beer = post.beer
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
        if post_id is None:
            return redirect('/beer/%d' % beer.id)
    return render_template('edit_post.html', form=form, new=post_id is None, uniqueid="post-%s" % post_id, post=post, beer=beer)


@app.route("/del/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def view_post_delete(post_id):
    post = Post.query.get(post_id)
    if post is None:
        raise NotFound('Post %d not found.' % post_id)
    if post.user_id != current_user.id and not current_user.admin:
        raise Forbidden('This is not your post to delete.')
    db.session.delete(post)
    db.session.commit()
    return redirect('/beer/%d' % post.beer_id)


@app.route("/admin")
@admin_required
def view_admin():
    if not current_user.admin:
        raise Forbidden('You are not an admin.')
    return render_template('admin.html', users=User.query.order_by(User.id).all())


@app.route("/edit/page/<int:page_id>", methods=['GET', 'POST'])
@app.route("/edit/page/", methods=['GET', 'POST'])
@admin_required
def view_page_edit(page_id=None):
    if not current_user.admin:
        raise Forbidden('You are not allowed to make or edit pages.')

    if page_id is None:
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
        db.session.refresh(page)
        if page_id is None:
            return redirect('/edit/page/%d' % page.id)
    return render_template('edit_page.html', form=form, title=page.title, uniqueid="page-%s" % page_id)


@app.route("/api/user/<int:user_id>/erase_bio", methods=['POST'])
@admin_required
def view_api_user_erase_bio(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User %d not found." % user_id)
    user.bio = ''
    user.bio_html = '<p class="text-danger">Your bio was erased by an admin.</p>'
    db.session.add(user)
    db.session.commit()
    return 'OK'


@app.route("/api/user/<int:user_id>/activate", methods=['POST'])
@admin_required
def view_api_user_activate(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User %d not found." % user_id)
    user.active = True
    db.session.add(user)
    db.session.commit()
    return 'OK'


@app.route("/api/user/<int:user_id>/admin", methods=['POST'])
@admin_required
def view_api_user_admin(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User %d not found." % user_id)
    if user.id == 1:
        raise BadRequest('You cannot un-admin the ÜberAdmin!')
    if current_user == user:
        raise BadRequest('You cannot un-admin yourself!')
    user.admin = not user.admin
    db.session.add(user)
    db.session.commit()
    return 'OK'


@app.route("/api/user/<int:user_id>/brewer", methods=['POST'])
@admin_required
def view_api_user_brewer(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User %d not found." % user_id)
    user.brewer = not user.brewer
    db.session.add(user)
    db.session.commit()
    return 'OK'



