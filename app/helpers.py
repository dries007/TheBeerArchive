from app import lm
from app import app
from flask_login import current_user
from CommonMark import commonmark


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.context_processor
def context_processor():
    return dict(user=current_user)


@app.template_filter('date')
def filter_date(datetime):
    return None if datetime is None else datetime.strftime('%-d %b %Y')


@app.template_filter('nl2br')
def filter_nl2br(text):
    return None if text is None else Markup('<br/>\n'.join(escape(text).splitlines()))


@app.template_filter('markdown')
def filter_markdown(text):
    return Markup(commonmark(re.sub('<.*?>', '', text)))
