
from xdm.plugins import *
from lib import requests
import hashlib
import json


baseURL = "http://api.trakt.tv/"
movieWatchlistURL = baseURL + "user/watchlist/movies.json/"
unwatchlistMovieURL = baseURL + "movie/unwatchlist/"

showWatchlistURL = baseURL + "user/watchlist/shows.json/"
unwatchlistShowURL = baseURL + "show/unwatchlist/"

class TraktWatchlist(MediaAdder):
    version = "0.3"
    identifier = "de.lad1337.traktwatchlist"
    addMediaTypeOptions = False
    screenName = 'Trakt Watchlist'
    _config = {'username': '',
               'password': '',
               'apikey': '',
               'remove_movies': True,
               'remove_shows': True}
    config_meta = {'plugin_desc': 'Add movies and TV shows from your http://trakt.tv account. Get your apikey at http://trakt.tv/settings/api',
                   'remove_movies': {'human': 'Remove movies after a successful add'},
                   'remove_shows': {'human': 'Remove tv shows after a successful add'}}

    types = ['de.lad1337.movies']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def runShedule(self):
        if not (self.c.username or self.c.password or self.c.apikey):
            return []
        movies = self._getWatchlist(movieWatchlistURL, self.c.username, self.c.password, self.c.apikey)
        out = []
        for movie in movies:
            additionalData = {}
            additionalData['tmdb_id'] = movie['tmdb_id']
            additionalData['imdb_id'] = movie['imdb_id']
            out.append(self.Media('de.lad1337.movies',
                                  movie['tmdb_id'],
                                  'tmdb',
                                  'Movie',
                                  movie['title'],
                                  additionalData=additionalData))

        shows = self._getWatchlist(showWatchlistURL, self.c.username, self.c.password, self.c.apikey)
        for show in shows:
            additionalData = {}
            additionalData['tvrage_id'] = show['tvrage_id']
            out.append(self.Media('de.lad1337.tv',
                                  show['tvdb_id'],
                                  'tvdb',
                                  'Show',
                                  show['title'],
                                  additionalData=additionalData))
        return out

    def successfulAdd(self, mediaList):
        """media list is a list off all the stuff to remove
        with the same objs that where returned in runShedule() """
        if self.c.remove_movies and len(mediaList):
            return self._removeFromWatchlist(self.c.username, self.c.password, self.c.apikey, mediaList)
        return True

    # get the movie watchlist
    def _getWatchlist(self, watchURL, username, password, apikey):
        url = self._makeURL(watchURL, apikey, username)
        log.debug("Calling trakt url: %s" % url, censor={apikey: 'apikey', username: 'username'})
        try:
            r = requests.get(url, auth=(username, self._hash(password)))
            return r.json()
        except:
            return []

    def _removeFromWatchlist(self, username, password, apikey, mediaList):
        result = True
        if self.c.remove_movies:
            traktMovieList = []
            for movie in mediaList:
                if movie.elementType == "Movie":
                    traktMovieList.append({'tmdb_id': movie.additionalData['tmdb_id'],
                                           'imdb_id': movie.additionalData['imdb_id']
                                           })
            result = self._removeItemsFromWatchlist(unwatchlistMovieURL, username, password, apikey, {"movies": traktMovieList})
        if self.c.remove_shows:
            traktShowList = []
            for show in mediaList:
                if show.elementType == "Show":
                    traktShowList.append({'tvdb_id': show.externalID})
            result = result == self._removeItemsFromWatchlist(unwatchlistShowURL, username, password, apikey, {"shows": traktShowList})
        return result

    def _removeItemsFromWatchlist(self, unwatchlistURL, username, password, apikey, traktData):
        url = self._makeURL(unwatchlistURL, apikey, "")
        log.info('Removing items from trakt watchlist %s' % traktData)
        postdata = {'username': username,
                    'password': self._hash(password)}
        postdata.update(traktData)
        try:
            r = requests.post(url, data=json.dumps(postdata))
            try:
                return r.json()['status'] == 'success'
            except ValueError:
                return False
        except:
            return False

    # construct the url
    def _makeURL(self, url, apiKey, username):
        result = url + apiKey
        if username != "":
            result += "/" + username
        return result

    # SHA1 hash
    def _hash(self, value):
        m = hashlib.sha1()
        m.update(value)
        return m.hexdigest()
