from migrate.versioning import api
from app import db
import os

db.create_all()

URI = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])

if not os.path.exists('db_repository'):
    api.create('db_repository', 'database repository')
    api.version_control(URI, 'db_repository')
else:
    api.version_control(URI, 'db_repository', api.version('db_repository'))
