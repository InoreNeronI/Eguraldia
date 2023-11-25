"""QApplication and QWebEngineView as done here:
    https://github.com/Widdershin/flask-desktop/blob/master/webui/webui.py
"""

from os import getenv
from socket import AF_INET, SOCK_STREAM, socket
from sys import argv, exit
from threading import Thread

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets


class UI:
    HOST = getenv(key='FLASK_RUN_HOST', default='127.0.0.1')
    PORT = getenv(key='FLASK_RUN_PORT')
    PROTOCOL = 'https' if getenv(key='FLASK_RUN_CERT') and getenv(key='FLASK_RUN_KEY') else 'http'

    def __init__(self, maximized=False):
        # create pyqt5 app and view
        self.qt_app = QtWidgets.QApplication(argv)
        self.qt_view = QtWebEngineWidgets.QWebEngineView(parent=self.qt_app.activeModalWidget())
        if maximized:
            self.show = self.qt_view.showMaximized
        else:
            self.show = self.qt_view.show

    def run(self, app):
        self.qt_app.setApplicationName(app.config.get('TITLE'))
        self.qt_app.setWindowIcon(QtGui.QIcon(app.config.get('ICON')))

        if not self.PORT:
            # @see https://stackoverflow.com/a/5089963
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind((self.HOST, 0))
            self.PORT = sock.getsockname()[1]
            sock.close()

        Thread(daemon=True, kwargs={'debug': app.debug,
                                    'host': self.HOST,
                                    'port': self.PORT,
                                    'threaded': True,
                                    'use_reloader': False}, target=app.run).start()

        self.qt_view.load(QtCore.QUrl('%s://%s:%s' % (self.PROTOCOL, self.HOST, self.PORT)))

        change_setting = self.qt_view.page().settings().setAttribute
        settings = QtWebEngineWidgets.QWebEngineSettings
        change_setting(settings.LocalStorageEnabled, True)
        change_setting(settings.PluginsEnabled, True)

        # show the view
        self.show()

        # start the pyqt5 app
        exit(self.qt_app.exec_())
