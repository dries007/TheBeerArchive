from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import mimetypes

mimetypes.init()
app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

#app.config.from_object(__name__ + '.Config')

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = '/login'

# Must be after init & config, to avoid circular dependencies
# Will show up as unused
import helpers
import models
import routes

