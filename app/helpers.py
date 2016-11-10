from app import lm
from app import app
from flask import Markup
from flask import request
from flask import escape
from flask_login import current_user
import CommonMark

from models import Config
from models import User
from models import Page
from models import Post


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.context_processor
def context_processor():
    return dict(user=current_user, config=Config.query.get(0).data)


@app.template_filter('date')
def filter_date(datetime):
    return None if datetime is None else datetime.strftime('%-d %b %Y')


@app.template_filter('nl2br')
def filter_nl2br(text):
    return None if text is None else Markup('<br/>\n'.join(escape(text).splitlines()))


@app.template_filter('markdown')
def filter_markdown(text):
    parser = CommonMark.Parser()
    renderer = CommonMark.HtmlRenderer({'softbreak': '<br />'})
    return Markup(renderer.render(parser.parse(text)))


def _test_menu_condition(condition):
    if condition['name'] == 'isurl':
        return condition.get('inverted', False) != (condition['data'] == request.path)
    elif condition['name'] == 'inurl':
        return condition.get('inverted', False) != (condition['data'] in request.path)
    elif condition['name'] == 'authenticated':
        return condition.get('inverted', False) != current_user.is_authenticated
    elif condition['name'] == 'active':
        return condition.get('inverted', False) != current_user.is_active
    elif condition['name'] == 'anonymous':
        return condition.get('inverted', False) != current_user.is_anonymous
    else:
        raise Exception('Condition unknown.', condition)
    pass


@app.template_test('menu_conditions')
def test_menu_conditions(item):
    if type(item) is str or 'conditions' not in item:
        return True
    return all(map(_test_menu_condition, item['conditions']))
