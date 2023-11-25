
from os import getenv


class Config:
    SECURITY_PASSWORD_HASH = getenv(key='SECURITY_PASSWORD_HASH', default='bcrypt')
    # Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
    SECURITY_PASSWORD_SALT = getenv(key='SECURITY_PASSWORD_SALT',
                                    default='246157207206506313353540320087937723641')
    SECURITY_CHANGEABLE = getenv(key='SECURITY_CHANGEABLE', default=True)
    SECURITY_CONFIRMABLE = getenv(key='SECURITY_CONFIRMABLE', default=True)
    SECURITY_REGISTERABLE = getenv(key='SECURITY_REGISTERABLE', default=True)
    SECURITY_RECOVERABLE = getenv(key='SECURITY_RECOVERABLE', default=True)
    SECURITY_TRACKABLE = getenv(key='SECURITY_TRACKABLE', default=True)
