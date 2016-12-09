import mimetypes

from flask import Flask
from flask_gravatar import Gravatar
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import os

mimetypes.init()

app = Flask(__name__)
# app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])
app.secret_key = os.environ['FLASK_SECRET']
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

lm = LoginManager(app)
lm.login_view = '/login'

gravatar = Gravatar(app, size=100, rating='g', default='mm', use_ssl=True)

# noinspection PyUnresolvedReferences
from uBlog import helpers, views, models, forms

# fixme: It's impossible to catch HTTPException. Flask Bug #941 (https://github.com/pallets/flask/issues/941)
from werkzeug.exceptions import default_exceptions
for code, ex in default_exceptions.items():
    app.errorhandler(code)(views.any_error)

