from flask import Markup
from flask import escape
from flask_login import current_user

from lxml.html import clean
from mdx_gfm import GithubFlavoredMarkdownExtension
import markdown
import humanize

from uBlog import lm, app
from uBlog.models import User, Page, Beer


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.context_processor
def context_processor():
    return dict(user=current_user, pages=Page.query.order_by(Page.id).all(), beers=Beer.query.order_by(Beer.id).all())


@app.template_filter('date')
def filter_date(datetime):
    return None if datetime is None else datetime.strftime('%-d %b %Y')


@app.template_filter('nl2br')
def filter_nl2br(text):
    return None if text is None else Markup('<br/>\n'.join(escape(text).splitlines()))


@app.template_filter('timedelta')
def filter_timedelta(datetime):
    return None if datetime is None else humanize.naturaltime(datetime)


class SimpleTextReplacePattern(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern, replacement):
        super().__init__(pattern)
        self.replacement = '%s%s;' % (markdown.util.AMP_SUBSTITUTE, replacement)

    def handleMatch(self, m):
        return self.replacement


class HTMLEntitiesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('copy', SimpleTextReplacePattern(r'\([cC]\)', 'copy'), '_end')
        md.inlinePatterns.add('reg', SimpleTextReplacePattern(r'\([rR]\)', 'reg'), '_end')
        md.inlinePatterns.add('phonogram_rights', SimpleTextReplacePattern(r'\([pP]\)', '#x2117'), '_end')
        md.inlinePatterns.add('trademark', SimpleTextReplacePattern(r'\([Tt][Mm]\)', 'trade'), '_end')
        md.inlinePatterns.add('plus_minus', SimpleTextReplacePattern(r'\+-', 'plusmn'), '_end')


def make_markdown(text, empty='<div class="md"></div>', clazz='md'):
    if text is None or text == '':
        return empty
    md = markdown.markdown(text, extensions=[GithubFlavoredMarkdownExtension(), HTMLEntitiesExtension()])
    cleaner = clean.Cleaner(links=False, add_nofollow=True)
    return '<div class="%s">%s</div>' % (clazz, cleaner.clean_html(md))


@app.template_filter('markdown')
def filter_markdown(text):
    return Markup(make_markdown(text))

# Nice idea in theory, too much work though
# def _test_menu_condition(condition):
#     if condition['name'] == 'isurl':
#         return condition.get('inverted', False) != (condition['data'] == request.path)
#     elif condition['name'] == 'inurl':
#         return condition.get('inverted', False) != (condition['data'] in request.path)
#     elif condition['name'] == 'authenticated':
#         return condition.get('inverted', False) != current_user.is_authenticated
#     elif condition['name'] == 'active':
#         return condition.get('inverted', False) != current_user.is_active
#     elif condition['name'] == 'anonymous':
#         return condition.get('inverted', False) != current_user.is_anonymous
#     else:
#         raise Exception('Condition unknown.', condition)
#     pass
#
#
# @app.template_test('menu_conditions')
# def test_menu_conditions(item):
#     if type(item) is str or 'conditions' not in item:
#         return True
#     return all(map(_test_menu_condition, item['conditions']))
