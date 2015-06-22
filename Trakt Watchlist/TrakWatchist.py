
from xdm.plugins import *
from easytrakt import Client
from easytrakt.models import MovieWatchlist
from easytrakt.models import ShowWatchlist

import logging


class TraktWatchlist(MediaAdder):
    version = "0.5"
    identifier = "de.lad1337.traktwatchlist"
    addMediaTypeOptions = False
    screenName = 'Trakt Watchlist'
    types = ['de.lad1337.movies']
    config_meta = {
        "plugin_desc": "Add movies and TV shows from your http://trakt.tv account."}
    oauth = None

    def __init__(self, instance='Default'):
        oauth_provider = common.PM.getPluginByIdentifier("de.lad1337.trakt.tv")
        if oauth_provider:
            self.oauth = oauth_provider.oauth
        MediaAdder.__init__(self, instance=instance)

        self.client = None
        if self.oauth and self.oauth.authorized:
            self.client = Client(self.oauth.session)

    def runShedule(self):
        if self.client is None:
            self.oauth.message_user_to_authenticate()
            return []
        movies_watchlist = MovieWatchlist(self.client)
        out = []
        for movie in movies_watchlist.items:
            additionalData = {
                "tmdb_id": movie.ids.tmdb,
                "imdb_id": movie.ids.imdb
            }
            out.append(
                self.Media(
                    'de.lad1337.movies',
                    movie.ids.tmdb,
                    'tmdb',
                    'Movie',
                    movie.title,
                    additionalData=additionalData)
            )

        show_watchlist = ShowWatchlist(self.client)
        for show in show_watchlist.items:
            out.append(
                self.Media(
                    'de.lad1337.tv',
                    show.ids.trakt,
                    'trakt',
                    'Show',
                    show.title
                )
            )
        return out
