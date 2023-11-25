
from os import getenv


class Config:
    GOOGLE_API_CLIENT_ID = getenv(key='GOOGLE_API_CLIENT_ID')
    GOOGLE_API_CLIENT_SECRET = getenv(key='GOOGLE_API_CLIENT_SECRET')
    TWITTER_API_CLIENT_ID = getenv(key='TWITTER_API_CLIENT_ID')
    TWITTER_API_CLIENT_SECRET = getenv(key='TWITTER_API_CLIENT_SECRET')
