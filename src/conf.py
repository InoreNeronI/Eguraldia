
from os import getenv, sep
from pathlib import Path

from werkzeug.utils import import_string

HERE = Path(__file__).parent.__str__()  # @see https://stackoverflow.com/a/56621841
ROOT_FOLDER = Path.cwd().__str__()
STATIC_FOLDER = getenv(key='STATIC_FOLDER', default=Path(ROOT_FOLDER).joinpath('public').__str__())
TEMPLATE_FOLDER = getenv(key='TEMPLATE_FOLDER', default=STATIC_FOLDER)


def files(src='', pattern='*.py'):
    return Path(HERE).joinpath(src).glob(pattern=pattern)


def import_file(src, verbose=False):
    parent = Path(src).parent.__str__().replace(HERE, '')[1:].replace(sep, '.')
    import_name = '%s.%s' % (parent, Path(src).stem)
    if verbose:
        print('\t`%s`...' % import_name)
    return import_string(import_name=import_name)


print('Loading configurations...')
inherits = []
for file in files(src='config'):
    inherits.append(import_file(src=file, verbose=True).Config)


class MixinConfig(*inherits):
    DEBUG = getenv(key='FLASK_DEBUG', default=False)
    ENV = getenv(key='FLASK_ENV', default='production')


class StageConfig(MixinConfig):
    DEBUG = getenv(key='FLASK_DEBUG', default=True)
    ENV = getenv(key='FLASK_ENV', default='development')
    SQLALCHEMY_ECHO = True


class TestingConfig(MixinConfig):
    ENV = getenv(key='FLASK_ENV', default='testing')
    TESTING = True
