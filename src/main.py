
"""Create an application instance or show a QWebEngineView.
    A very recommendable read is here:
        https://hackingandslacking.com/demystifying-flasks-application-context-c7bd31a53817"""


# Include dependencies. @see https://stackoverflow.com/a/56999264
def include():
    from os import getenv
    from pathlib import Path
    from sys import path, version

    if __name__ == '__main__' or 'gunicorn' in getenv(key='_') or 'uwsgi' in getenv(key='_'):
        path.append(Path.cwd().joinpath('__pypackages__', version[:4], 'lib').__str__())
        if not getenv(key='FLASK_SKIP_DOTENV'):
            from dotenv import load_dotenv

            load_dotenv(dotenv_path='.env')
    if '.' in __name__:
        path.append(Path.cwd().joinpath('src').__str__())


def load(config_object=None):
    include()
    from util.main import app, boot
    boot(conf_obj=config_object)

    return app


app = load()

if __name__ == '__main__':
    from util.ui import UI
    UI().run(app=app)
