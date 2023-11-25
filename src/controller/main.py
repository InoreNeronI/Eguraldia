
# from locale import LC_ALL, getdefaultlocale, setlocale
from datetime import date, datetime, time, timedelta
from mimetypes import guess_type
from os import getenv
from pathlib import Path

from babel.dates import format_date, format_time
from flask.globals import current_app, request, session
from flask.helpers import flash, send_from_directory
from flask.templating import render_template, render_template_string
from flask_babel import _
from jinja2.exceptions import TemplateNotFound
from pandas import to_datetime
from simhash import Simhash
from sqlalchemy.exc import IntegrityError, ProgrammingError
from werkzeug.utils import redirect

from conf import ROOT_FOLDER
from model.main import Text
from util.extensions import db, defaults, translator
from util.translator import GoogleTranslatorError

favicon = current_app.config.get('ICON')
defaults.update({'icon': '/static/' + Path(favicon).name,
                 'icon_type': current_app.config.get('ICON_TYPE'),
                 'languages': current_app.config.get('LANGUAGES'),
                 'title': current_app.config.get('TITLE'),
                 'placekit_api_key': current_app.config.get('PLACEKIT_API_KEY')})


def days():
    today = date.today()
    now = datetime.strptime(request.args.get('d'), '%m/%d/%y') if request.args.get('d') else today
    defaults.update({'days': {'after': get_date(d=now + timedelta(days=1)),
                              'before': get_date(d=now - timedelta(days=1)),
                              'now': get_date(d=now),
                              'today': get_date(d=today),
                              'tomorrow': get_date(d=today + timedelta(days=1)),
                              'next': get_date(d=today + timedelta(days=2))}})


def get_date(d, f='short', l='en'):
    return format_date(date=d, format=f, locale=l)


def icon(filename=None, parent=Path(getenv(key='HOME')).joinpath('Downloads').__str__() if getenv(key='HOME') else ROOT_FOLDER):
    """Render resource from '~/Downloads/FILE' or render the favicon by default."""
    directory = Path(parent).joinpath(filename).parent.__str__() if filename else Path(favicon).parent.__str__()
    filename = Path(filename if filename else favicon).name
    mimetype = guess_type(url=Path(directory).joinpath(filename).__str__())[0] if filename else defaults.get('icon_type')

    return send_from_directory(directory=directory, filename=filename, mimetype=mimetype)


def language():
    return session.get('language') if 'language' in session else request.accept_languages.best_match(matches=defaults.get('languages').keys())


def locale(default='en'):
    """Set requested or matched language."""
    lc = request.args.get('l')
    if not lc:
        # session['language'] = getdefaultlocale()[0]
        lc = language()
    elif lc[:2] not in defaults.get('languages').keys():
        flash(_('"%s" language is not supported.') % lc, 'warning')
        lc = language()

    if 'language' not in session:
        try:
            session['language'] = lc[:2]
        except TypeError:
            session['language'] = default
    elif lc[:2] != session.get('language'):
        # setlocale(category=LC_ALL, locale=[lc, 'UTF-8'])
        session['language'] = lc[:2]
        flash(_('Enjoy %s ッ') % defaults.get('languages').get(session.get('language')), 'info')

    defaults['language'] = session.get('language')
    current_app.config['RECAPTCHA_PARAMETERS'] = dict(hl=defaults.get('language'))


def render(*args, **kwargs):
    return render_template(*args, **{**defaults, **kwargs})


def skin():
    """Invert theme if requested or choose light by default."""
    skins = ['light', 'dark']
    if request.args.get('t'):
        skins.remove(request.args.get('t'))
        if session.get('theme') != skins[0]:
            session['theme'] = skins[0]
            flash(_('Enjoy daylight ッ') if session.get('theme') == 'light' else _('Enjoy nightlight ッ'), 'info')
    defaults['theme'] = session.get('theme') if 'theme' in session else skins[0]
    prev_skin = ['light', 'dark']
    prev_skin.remove(defaults.get('theme'))
    defaults['icon'] = defaults.get('icon').replace(prev_skin[0], defaults.get('theme'))
    current_app.config['RECAPTCHA_DATA_ATTRS'] = dict(theme=defaults.get('theme'))


def start(segment, **kwargs):
    """Render the html file from static/FILE if exists or render static/__404.html"""
    try:
        return render_template(template_name_or_list=segment, **defaults, **kwargs)

    except TemplateNotFound:
        return render_template(template_name_or_list='__404.html', **defaults, **kwargs), 404


def stop():
    """Stop the werkzeug server (disabled in production)."""
    if current_app.debug:
        if 'werkzeug.server.shutdown' not in request.environ:
            raise RuntimeError(_('Werkzeug server is not running.'))

        request.environ.get('werkzeug.server.shutdown')()

        return _('Server shutting down...')
    else:
        redirect(location='/')


def translate(default=defaults.get('language')):
    """Render translation from Google with `py-googletrans` and try to cache it in database."""
    text = request.args.get('text')
    if not text:
        raise RuntimeError(_('Text is mandatory.'))

    dest_lang = request.args.get('dest') if request.args.get('dest') else default
    src_lang = request.args.get('src') if request.args.get('src') else 'auto'

    if dest_lang == src_lang:
        dest_text = text
    else:
        # @see https://medium.com/better-programming/how-to-hash-in-python-8bf181806141
        hash = Simhash(value=text).value.__str__() + '-' + dest_lang
        kwargs = {'lang_src': src_lang, 'lang_tgt': dest_lang, 'text': text}
        try:
            dest_text = db.session.query(Text).get(hash)
            if dest_text is None:
                try:
                    dest_text = translator.translate(**kwargs)
                    db.session.add(instance=Text(hash, dest_text))
                    db.session.commit()
                except (AttributeError, GoogleTranslatorError):
                    dest_text = ''
            else:
                dest_text = dest_text.text
        except (IntegrityError, ProgrammingError):
            try:
                dest_text = translator.translate(**kwargs)
            except (AttributeError, GoogleTranslatorError):
                dest_text = ''

    return render_template_string(source=dest_text)


def translate_date(default=defaults.get('language')):
    """Parse/translate a date."""
    d = request.args.get('date')
    if not d:
        raise RuntimeError(_('Date is mandatory.'))

    dest_lang = request.args.get('dest') if request.args.get('dest') else default
    variation = request.args.get('variation') if request.args.get('variation') else 'short'

    d_list = d.split('/')
    if request.args.get('src') == 'es':
        d = date(year=int(d_list[2]), month=int(d_list[1]), day=int(d_list[0]))
    else:
        d = date(*d_list)

    return render_template_string(source=get_date(d=d, f=variation, l=dest_lang))


def translate_time(default=defaults.get('language')):
    """Parse/translate a date, @see https://stackoverflow.com/a/51235728"""
    t = request.args.get('time')
    if not t:
        raise RuntimeError(_('Time is mandatory.'))

    dest_lang = request.args.get('dest') if request.args.get('dest') else default
    src = request.args.get('src')
    variation = request.args.get('variation') if request.args.get('variation') else 'short'

    t_list = t.split(':')
    if variation == 'short' and len(t_list) == 3 and t_list[2].index('00') == 0:
        t = t_list[0] + ':' + t_list[1] + t_list[2][2:]

    if src == 'en':
        dest_format = '%I:%M %p' if variation == 'short' else '%I:%M:%S %p'
    else:
        dest_format = '%H:%M' if variation == 'short' else '%H:%M:%S'

    timestamp = to_datetime(t, format=dest_format)
    t = timestamp.__str__()[timestamp.__str__().index(' ') + 1:]
    t_list = t.split(':')

    if variation == 'short':
        t = time(hour=int(t_list[0]), minute=int(t_list[1]))
    else:
        t = time(hour=int(t_list[0]), minute=int(t_list[1]), second=int(t_list[2]))

    return render_template_string(source=format_time(time=t, format=variation, locale=dest_lang))
