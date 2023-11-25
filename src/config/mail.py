
from os import getenv


class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = getenv(key='GMAIL_USER')
    MAIL_PASSWORD = getenv(key='GMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = None
    RECAPTCHA_PRIVATE_KEY = getenv(key='RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_PUBLIC_KEY = getenv(key='RECAPTCHA_PUBLIC_KEY')
