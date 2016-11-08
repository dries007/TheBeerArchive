import imp
from migrate.versioning import api
from app import db
import os

URI = 'postgresql://%s:%s@db/%s' % (os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB'])

v = api.db_version(URI, 'db_repository')
migration = 'db_repository' + ('/versions/%03d_migration.py' % (v+1))
tmp_module = imp.new_module('old_model')
old_model = api.create_model(URI, 'db_repository')
exec(old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(URI, 'db_repository', tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(URI, 'db_repository')
v = api.db_version(URI, 'db_repository')
print('New migration saved as ' + migration)
print('Current database version: ' + str(v))
