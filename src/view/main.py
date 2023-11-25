
from flask.globals import current_app

from controller.main import (days, icon, locale, skin, start, stop, translate,
                             translate_date, translate_time)

"""Add locale, skin."""
# @see https://www.reddit.com/r/flask/comments/apwtm9/flask_blueprints_and_before_request
current_app.before_request_funcs = {None: [days, locale, skin]}

"""Add example route."""
current_app.add_url_rule(rule='/icon', endpoint='icon_default', view_func=icon)
current_app.add_url_rule(rule='/icon/<path:filename>', endpoint='icon', view_func=icon)

"""Add main route (generic routing)."""
# @see https://github.com/app-generator/jinja-template-volt-dashboard/blob/master/app/views.py
current_app.add_url_rule(rule='/', defaults={'segment': '__place.html'},
                         endpoint='start_default', view_func=start)
current_app.add_url_rule(rule='/<path:segment>', endpoint='start', view_func=start)

"""Add shutdown route."""
current_app.add_url_rule(rule='/shutdown', endpoint='stop', methods=['POST'], view_func=stop)

"""Add Google translate service route."""
current_app.add_url_rule(rule='/translate', endpoint='translate', view_func=translate)

"""Add date translation route."""
current_app.add_url_rule(rule='/translate-date', endpoint='translate_date', view_func=translate_date)

"""Add time translation route."""
current_app.add_url_rule(rule='/translate-time', endpoint='translate_time', view_func=translate_time)
