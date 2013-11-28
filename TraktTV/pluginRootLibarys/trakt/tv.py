import hashlib
import os
from trakt.api import *
calendar = Calendar
search = Search
server = Server
show = Show
shows = Shows


def setup(apikey=None, username=None, password=None):
    if apikey:
        os.environ['TRAKT_APIKEY'] = apikey
    if username:
        os.environ['TRAKT_USERNAME'] = username
    if password:
        os.environ['TRAKT_PASSWORD'] = hashlib.sha1(password.encode('utf-8')).hexdigest()


def reset():
    for var in ('TRAKT_APIKEY', 'TRAKT_USERNAME', 'TRAKT_PASSWORD'):
        if var in os.environ:
            del os.environ[var]
