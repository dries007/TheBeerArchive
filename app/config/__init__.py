import os

SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])
SECRET_KEY = os.environ['FLASK_SECRET']

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_PORT = int(os.environ['MAIL_PORT'])
MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
MAIL_USE_SSL = os.environ['MAIL_USE_SSL']

# These messages gets parsed by jinja first, then it gets markdownified to become HTML

MAIL_TEMPLATE_ACTIVATION = """Hi {{ user.name }},

You recently registered an account on https://bier.dries007.net .
To activate your account you need to go to this URL: https://bier.dries007.net/register/{{ user.id }}/{{ token }} .

If it was not you who registered this account, take no action. The record will be deleted after 36 hours.

Greetings,
The electrons running Dries007.net

Ps: This is a no-reply email address. Any reply received will be automatically deleted.
"""

MAIL_TEMPLATE_RESET = """Hi {{ user.name }},

You recently requested a password reset on https://bier.dries007.net .
Here is the password reset URL: https://bier.dries007.net/login/reset/{{ user.id }}/{{ token }} .

If you did not request this reset, take no action. The token only lasts for 24 hours.

Greetings,
The electrons running Dries007.net

Ps: This is a no-reply email address. Any reply received will be automatically deleted.
"""