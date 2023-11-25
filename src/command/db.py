"""Database related click commands."""

from os import environ
from subprocess import run
from tempfile import TemporaryDirectory

from alembic.command import upgrade
from click import command, echo, option
from flask.cli import with_appcontext
from flask.globals import current_app
from flask_migrate import Migrate

from conf import files, import_file
from model.main import Mail, Role, Text, User
from util.extensions import db


def data():
    return current_app.config.get('SQLALCHEMY_DATA')


@command(short_help='Drop database.')
@with_appcontext
def drop(temp_dir=TemporaryDirectory()):
    echo('Dropping data...')
    echo('\t... %d mails' % Mail.query.count())
    echo('\t... %d roles' % Role.query.count())
    echo('\t... %d texts' % Text.query.count())
    echo('\t... %d users' % User.query.count())
    db.drop_all()
    temp_dir.cleanup()
    if 'ALCHEMYDUMDIR' in environ:
        del environ['ALCHEMYDUMDIR']


@command(short_help='Create database.')
@option('-f', '--fixtures', default=False, help='Load initial data into database.',
        is_flag=True)
@with_appcontext
def init(fixtures):
    """Initialize the database."""
    echo('Creating tables for `%s@%s`' % (data()['user'], data()['db']))
    # Import all modules here that might define models so that they will be registered properly
    # on the metadata, otherwise you will have to import them first before calling create_all()
    # @see https://stackoverflow.com/a/20749534
#    print('Loading models...')
#    for file in files(src='model'):
#        import_file(src=file, verbose=True)
    db.create_all()
    if fixtures:
        load_fixtures()
    return db.session.commit()


@command(short_help='Load initial data into database.')
@with_appcontext
def load():
    """Load initial data to the database."""
    load_fixtures()
    return db.session.commit()


def load_fixtures():
    echo('Loading fixtures...')
    for file in files(src='fixture'):
        import_file(src=file, verbose=True)


@command(short_help='Apply migrations into database.')
@with_appcontext  # @see https://stackoverflow.com/a/46541219
def migrate():
    """Apply migrations to the database with alembic."""
    return upgrade(config=Migrate(app=current_app, db=db).get_config(), revision='head')


@command(short_help='Login into database shell, \'psql\' needs to be installed.')
@with_appcontext
def shell():
    """Login into database shell."""
    environ['PGPASSWORD'] = data()['pw']
    return exit(run('psql -d {db} -U {user} -h {host} -p {port}'.format(**data()), shell=True))


@command(short_help='Show database connection string.')
@with_appcontext
def url():
    """Show database connection string."""
    return echo(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
