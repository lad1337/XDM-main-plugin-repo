import os
try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus
import requests
from trakt.errors import TraktException
__all__ = (
    'Shows',
    'Calendar',
    'Server',
    'Search',
    'Show',
)


class AbstractApi(object):
    @classmethod
    def _get(cls, api, *args):
        auth = None
        if os.getenv('TRAKT_USERNAME') and os.getenv('TRAKT_PASSWORD'):
            auth = (os.getenv('TRAKT_USERNAME'), os.getenv('TRAKT_PASSWORD'))
        #print cls._builduri(api, *args)
        response = requests.get(cls._builduri(api, *args), auth=auth).json()
        if isinstance(response, dict) and response.get('status', False) == 'failure':
            raise TraktException(response.get('error', 'Unknown Error'))
        return response

    @staticmethod
    def _builduri(api, *args):
        """
        >>> AbstractApi._builduri('/shows/trending/', None)
        'http://api.trakt.tv/shows/trending.json/TRAKTAPIKEY'
        """
        return '{0}/{1}.{2}/{3}/{4}'.format(
            'http://api.trakt.tv',
            api.strip('/'),
            'json',
            os.getenv('TRAKT_APIKEY', 'TRAKTAPIKEY'),
            '/'.join(map(str, filter(lambda item: item or item == 0, args)))
        ).rstrip('/')


class Shows(AbstractApi):
    @classmethod
    def trending(cls):
        """
        Returns all shows being watched right now.

        """
        return cls._get('shows/trending')

    @classmethod
    def updated(cls, timestamp=None):
        """
        Returns all shows updated since a timestamp.
        The server time is in PST.
        To establish a baseline timestamp, you can use the Server.time() method.

        :param timestamp: Start with this timestamp and find anything updated since then.
        """
        return cls._get('shows/updated', timestamp)


class Calendar(AbstractApi):
    @classmethod
    def shows(cls, date=None, days=None):
        """
        Returns all shows airing during the time period specified.

        :param date: Start date for the calendar. (today)
        :param days: Number of days to display starting from the date. (7)
        """
        if date:
            date = date.strftime('%Y%m%d')
        else:
            days = None
        return cls._get('calendar/shows', date, days)

    @classmethod
    def premieres(cls, date=None, days=None):
        """
        Returns all shows premiering during the time period specified.

        :param date: Start date for the calendar. (today)
        :param days: Number of days to display starting from the date. (7)
        """
        if date:
            date = date.strftime('%Y%m%d')
        else:
            days = None
        return cls._get('calendar/premieres', date, days)


class Server(AbstractApi):
    @classmethod
    def time(cls):
        """
        Get the current timestamp and timezone for the trakt server.
        """
        return cls._get('server/time')


class Search(AbstractApi):
    @classmethod
    def shows(cls, query):
        """
        Search for tv shows.

        :param query: The search query that should be used
        """
        if isinstance(query, (str, unicode)):
            query = quote_plus(query.encode('utf8'))
        return cls._get('search/shows', query)


class Show(AbstractApi):
    @classmethod
    def episode(cls, title, season, episode):
        """
        Returns information for an episode

        :param title: Either the slug (i.e. the-walking-dead) or TVDB ID
        :param season: The season number. Use 0 if you want the specials
        :param episode: The episode number
        """
        return cls._get('show/episode/summary', title, season, episode)

    @classmethod
    def related(cls, title, hidewatched=False):
        """
        Get the top 10 related shows

        :param title: Either the slug (i.e. the-walking-dead) or TVDB ID
        :param hidewatched: If this parameter is set and valid auth is sent,
        shows with at least one play will be filtered out (False)
        """
        hidewatched = 'hidewatched' if hidewatched else None
        return cls._get('show/related', title, hidewatched)

    @classmethod
    def season(cls, title, season):
        """
        Returns detailed episode info for a specific season of a show.

        :param title: Either the slug (i.e. the-walking-dead) or TVDB ID
        :param season: The season number. Use 0 if you want the specials
        """
        return cls._get('show/season', title, season)

    @classmethod
    def seasons(cls, title):
        """
        Returns basic season info for a show.

        :param title: Either the slug (i.e. the-walking-dead) or TVDB ID
        """
        return cls._get('show/seasons', title)

    @classmethod
    def summary(cls, title, extendend=False):
        """
        Returns information for a TV show including ratings, top watchers, and most watched episodes.

        :param title: Either the slug (i.e. the-walking-dead) or TVDB ID
        :param extendend: Returns complete season and episode info (False)
        """
        extendend = 'extended' if extendend else None
        return cls._get('show/summary', title, extendend)
