
from xdm.plugins import *
from lib import requests
import csv

class ImdbWatchlist(MediaAdder):
    version = "0.1"
    identifier = "de.lad1337.imdbwatchlist"
    addMediaTypeOptions = False
    screenName = 'IMDb Watchlist'
    _config = {'watchlist_url': ''}
    config_meta = {'plugin_desc': 'Add movies from your http://www.imdb.com watchlist.',
                   'watchlist_url': {'human': 'URL of your CSV watchlist on IMDb'}}

    types = ['de.lad1337.movies']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def runShedule(self):
        if not (self.c.watchlist_url):
            return []
        movies = self._getImdbWatchlist()
        out = []
        for movie in movies:
            additionalData = {}
            additionalData['imdb_id'] = movie['imdb_id']
            out.append(self.Media('de.lad1337.movies',
                                  movie['imdb_id'],
                                  'tmdb',
                                  'Movie',
                                  unicode(movie['title'], 'utf-8'),
                                  additionalData=additionalData))
        return out

    def _utf8Encoder(self, unicodeCsvData):
        for line in unicodeCsvData:
            yield line.encode('utf-8')

    # get movie watchlist
    def _getImdbWatchlist(self):        
        try:
            r = requests.get(self.c.watchlist_url)
            r.encoding = 'utf-8'
            csvReader = csv.reader(self._utf8Encoder(r.text.splitlines()), dialect=csv.excel)
            header = csvReader.next()
            colId = header.index('const')
            colTitle = header.index('Title')
            movies = []
            for row in csvReader:
                movies.append({'imdb_id':row[colId], 'title':row[colTitle]})
            return movies
        except Exception:
            return []
