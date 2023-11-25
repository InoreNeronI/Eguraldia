"""An application factory, as explained here:
    https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories
"""

from logging import StreamHandler, basicConfig
from mimetypes import guess_type
from pathlib import Path
from sys import stdout
from urllib.parse import urlencode as url_encode

from flask.app import Flask
from flask.cli import AppGroup
from flask.globals import g
from flask.helpers import flash, get_debug_flag, request, session
from flask.templating import render_template
from flask_babel import Babel, _
from werkzeug.exceptions import BadRequest

from command.db import drop, init, load, migrate, shell, url
from command.main import lint
from conf import (STATIC_FOLDER, TEMPLATE_FOLDER, MixinConfig, StageConfig,
                  files, import_file)
from util.extensions import (alchemydumps, babel, db, defaults, mail, migrator,
                             security)

app = Flask(import_name=__name__, static_folder=STATIC_FOLDER, static_url_path='/static',
            template_folder=TEMPLATE_FOLDER)


# @see https://github.com/Flask-Middleware/flask-security/issues/108
# @see https://stackoverflow.com/a/35938557/16711967
def get_locale():
    # if a user is logged in, use the locale from the user settings
    identity = getattr(g, 'identity', None)
    if identity is not None and identity.id:
        return identity.user.locale
    with app.request_context({'wsgi.url_scheme': "", 'SERVER_PORT': "", 'SERVER_NAME': "", 'REQUEST_METHOD': ""}):
        return session.get('language')


def get_timezone():
    identity = getattr(g, 'identity', None)
    if identity is not None and identity.id:
        return identity.user.timezone


def boot(a=app, conf_obj=None):
    """Part of the work is based on these files:
        https://flask.palletsprojects.com/en/1.1.x/appcontext/#manually-push-a-context
        https://github.com/gothinkster/flask-realworld-example-app/blob/master/autoapp.py
        https://github.com/gothinkster/flask-realworld-example-app/blob/master/conduit/commands.py

    :param a: The app object to use.
    :param conf_obj: The configuration object to use.
    """
    if not conf_obj:
        conf_obj = StageConfig if get_debug_flag() else MixinConfig
    a.config.from_object(obj=conf_obj)
    a.url_map.strict_slashes = False

    register_commands()
    register_error_handlers()
    register_extensions()

    # @see https://stackoverflow.com/q/25860304
    @a.after_request
    def add_header(response):
        filename = Path(STATIC_FOLDER).joinpath(request.path[1:]).__str__()
        if Path(filename).is_file():
            response.headers['Content-Type'] = guess_type(url=filename)[0] + '; charset=utf-8'
        return response

    # @see https://stackoverflow.com/a/31411495
    @a.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

    # @see https://stackoverflow.com/a/31121430
    @a.template_global()
    def get_query(**new_values):
        args = request.args.copy()

        for key, value in new_values.items():
            args[key] = value

        return '{}?{}'.format(request.path, url_encode(args))


# @see https://stackoverflow.com/a/63087331
def register_commands(a=app, cli=AppGroup(help='Perform postgres operations.', name='postgres')):
    """Register production commands."""
    a.cli.add_command(cmd=cli, name='ps')
    cli.add_command(cmd=drop, name='drop')
    cli.add_command(cmd=init, name='init')
    cli.add_command(cmd=load, name='load')
    cli.add_command(cmd=migrate, name='migrate')
    cli.add_command(cmd=shell, name='shell')
    cli.add_command(cmd=url, name='url')
    if a.debug:
        """Register development commands."""
        a.cli.add_command(cmd=lint)
    if not a.logger.handlers:
        """Configure logger."""
        a.logger.addHandler(hdlr=StreamHandler(stream=stdout))


def register_error_handlers(a=app):
    """Register error handlers."""
    # @see https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling
    @a.errorhandler(500)
    def handle_internal(error):
        db.session.rollback()
        flash(_('Error: %s') % error, 'error')
        return render_template(template_name_or_list='__500.html', **defaults), 500

    if not a.debug:
        @a.errorhandler(BadRequest)
        def handle_bad_request(error):
            basicConfig()
            flash(_('Bad request: %s') % error, 'error')
            return render_template(template_name_or_list='__500.html', **defaults), 500

        @a.errorhandler(Exception)
        def handle_exception(error):
            basicConfig()
            flash(_('Unhandled exception: %s') % error, 'error')
            return render_template(template_name_or_list='__500.html', **defaults), 500


def register_extensions(a=app):
    """Register Flask extensions."""
    # Init AlchemyDumps
    alchemydumps.init_app(app=a, db=db)
    # Init Babel
    babel.init_app(app=app, locale_selector=get_locale, timezone_selector=get_timezone)
    # Init SQLAlchemy
    db.init_app(app=a)
    # Init Mail
    mail.init_app(app=a)
    # Init Migrate
    migrator.init_app(app=a, db=db)
    # Init Security and load routes from views folder
    with a.app_context():
        from controller.main import render
        from util.db import store
        """Init security and register its blueprint with its defaults."""
        security.init_app(app=a, datastore=store, register_blueprint=True,
                          render_template=render)
        """Register routes."""
        print('Loading routes...')
        for file in files(src='view'):
            import_file(src=file, verbose=True)
