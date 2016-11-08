from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import mimetypes
import os

mimetypes.init()
app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

#app.config.from_object(__name__ + '.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = '/login'

# Must be after init & config, to avoid circular dependencies
# Will show up as unused
import helpers
import models
import routes

