import datetime
import sys

from sqlalchemy import Integer, and_

from uBlog import db, app, scheduler
from uBlog.models import User


@scheduler.scheduled_job('interval', id='remove_stale_users', hours=1)
def task_remove_stale_users():
    print('Stale user purge', file=sys.stderr)
    with app.app_context():
        to_remove = User.query.filter(and_(User.active.is_(False), datetime.datetime.now() - User.registered_on > datetime.timedelta(days=3))).all()
        removed = []
        for user in to_remove:
            removed.append(dict(id=user.id, name=user.name))
            db.session.delete(user)
        db.session.commit()
        print('removed users', removed, file=sys.stderr)


@scheduler.scheduled_job('interval', id='remove_stale_reset_tokens', hours=1)
def task_remove_stale_reset_tokens():
    print('Stale reset token purge', file=sys.stderr)
    now = datetime.datetime.now().timestamp()
    with app.app_context():
        users = User.query.filter(and_(User.json.has_key('reset_token'), User.json['reset_token_expire'].astext.cast(Integer) < int(now))).all()
        removed = []
        for user in users:
            removed.append(user.name)
            del user.json['reset_token']
            del user.json['reset_token_expire']
            db.session.add(user)
        db.session.commit()
        print('removed reset tokens', removed, file=sys.stderr)
