import os

SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@localhost/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])
SECRET_KEY = os.environ['FLASK_SECRET']

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
GOOGLE_ANALYTICS = os.environ['GOOGLE_ANALYTICS'] or None

MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_PORT = int(os.environ['MAIL_PORT'])
MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
MAIL_USE_SSL = os.environ['MAIL_USE_SSL']

# These messages gets parsed by jinja first, then it gets markdownified to become HTML

with open(os.path.dirname(__file__) + '/activation_email.md') as f:
    MAIL_TEMPLATE_ACTIVATION = f.read()

with open(os.path.dirname(__file__) + '/reset_email.md') as f:
    MAIL_TEMPLATE_RESET = f.read()

