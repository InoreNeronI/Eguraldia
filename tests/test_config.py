
from flask.app import Flask

from conf import MixinConfig, StageConfig, TestingConfig
from util.main import (register_commands, register_error_handlers,
                       register_extensions)


def config(app, obj):
    app.config.from_object(obj=obj)
    register_commands(a=app)
    register_error_handlers(a=app)
    register_extensions(a=app)


def test_development_config():
    """Development config."""
    app = Flask(import_name='test_development_config')
    config(app=app, obj=StageConfig)
    assert app.config.get('DEBUG')
    assert app.config.get('ENV') == 'development'
    assert not app.config.get('TESTING')


def test_production_config():
    """Production config."""
    app = Flask(import_name='test_production_config')
    config(app=app, obj=MixinConfig)
    assert app.config.get('ENV') == 'production'
    assert not app.config.get('DEBUG')
    assert not app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    assert not app.config.get('TESTING')


def test_testing_config():
    """Testing config."""
    app = Flask(import_name='test_testing_config')
    config(app=app, obj=TestingConfig)
    assert app.config.get('ENV') == 'testing'
    assert app.config.get('TESTING')
    assert not app.config.get('DEBUG')
