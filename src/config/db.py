
from os import getenv
from subprocess import check_output

from conf import ROOT_FOLDER


def output(cmd, verbose=False):
    out = check_output(cmd, cwd=ROOT_FOLDER, shell=True).__str__()
    if verbose:
        print(out)
    try:
        end = out.rindex('make')
    except ValueError:
        end = out.rindex('\'')
    start = out.rindex('\\n', 0, end) + 2
    return out[start:end]


class Config:
    SQLALCHEMY_DATA = {
        'db': getenv(key='POSTGRES_DB', default='postgres'),
        'host': getenv(key='POSTGRES_HOST', default=output(cmd='make ip')),
        'port': getenv(key='POSTGRES_PORT', default=output(cmd='make port')),
        'pw': getenv(key='POSTGRES_PASSWORD'),
        'user': getenv(key='POSTGRES_USER', default='postgres')}
    # @see https://stackoverflow.com/a/66826111/16711967
    SQLALCHEMY_DATABASE_URI =\
        'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(**SQLALCHEMY_DATA)
    # As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the underlying engine.
    # This option makes sure that DB connections from the pool are still valid.
    # It is important since many DBaaS options automatically close idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
