import os

SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])
SECRET_KEY = os.environ['FLASK_SECRET']

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
