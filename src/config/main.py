
from mimetypes import guess_type
from os import getenv
from pathlib import Path
from secrets import token_urlsafe

from conf import ROOT_FOLDER


class Config:
    # @see https://stackoverflow.com/a/42750648
    BABEL_TRANSLATION_DIRECTORIES = Path(ROOT_FOLDER).joinpath('translations').__str__()
    ICON = getenv(key='FLASK_ICON', default=Path(ROOT_FOLDER).joinpath('static', 'favicon-dark.svg').__str__())
    ICON_TYPE = guess_type(url=ICON)[0]
    LANGUAGES = {'en': 'English', 'es': 'Español', 'eu': 'Euskara', 'fr': 'Français'}
    SECRET_KEY = getenv(key='SECRET_KEY', default=token_urlsafe())
    TITLE = getenv(key='FLASK_TITLE', default=Path(ROOT_FOLDER).name)
