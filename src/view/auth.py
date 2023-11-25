
from flask.globals import current_app

from controller.auth import Auth

"""Add Google sign route."""
current_app.add_url_rule(rule='/auth/<provider_name>/', endpoint='auth', view_func=Auth.as_view(name='auth'))
