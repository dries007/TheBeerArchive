from flask import render_template
from flask import abort
from app import app

from models import *


@app.route("/")
def hello():
    page = Page.query.filter_by(name='index').first()
    if page is None:
        abort(404)
    return render_template('page.html', page=page)
