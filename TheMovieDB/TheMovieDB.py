# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://github.com/lad1337/XDM
#
# This file is part of XDM: eXtentable Download Manager.
#
# XDM: eXtentable Download Manager. Plugin based media collection manager.
# Copyright (C) 2013  Dennis Lutter
#
# XDM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# XDM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from xdm.plugins import *
from dateutil.parser import *
import tmdb


class Tmdb(Provider):
    version = "0.13"
    identifier = "de.lad1337.tmdb"
    _tag = 'tmdb'
    screenName = 'TheMovieDB'
    single = True
    types = ['de.lad1337.movies']
    _config = {'enabled': True,
               'img_size_select': 'm',
               'info_language_select': 'en'}

    config_meta = {'plugin_desc': 'Movie information from http://www.themoviedb.org/.'}

    def __init__(self, instance='Default'):
        Provider.__init__(self, instance=instance)
        tmdb.configure('5c235bb1b487932ebf0a9935c8b39b0a', self.c.info_language_select)

    @profileMeMaybe
    def searchForElement(self, term=''):
        self.progress.reset()
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.movies')
        mtm = common.PM.getMediaTypeManager('de.lad1337.movies')[0]
        fakeRoot = mtm.getFakeRoot(term)

        movies = tmdb.Movies(term, limit=True)

        self.progress.total = movies.get_total_results()
        for tmdbMovie in movies:
            self.progress.addItem()
            self._createMovie(fakeRoot, mediaType, tmdbMovie)

        return fakeRoot

    def _img_size_select(self):
        return {'o': 'Orginal size (slow web page)',
                'l': 'Large 500px wide',
                'm': 'Medium 185px wide',
                's': 'Small 92px wide'}

    def _info_language_select(self):
        return {"de": "Deutsch",
                "en": "English",
                "es": "Spanish",
                "fr": "French"}

    def _createMovie(self, fakeRoot, mediaType, tmdbMovie):
        movie = Element()
        movie.mediaType = mediaType
        movie.parent = fakeRoot
        movie.type = 'Movie'
        movie.setField('name', tmdbMovie.get_title(), self.tag)
        rl_date = tmdbMovie.get_release_date()
        if len(rl_date.split('-')) > 1:
            movie.setField('year', rl_date.split('-')[0], self.tag)
        else:
            movie.setField('year', 0, self.tag)
        movie.setField('poster_image', tmdbMovie.get_poster(img_size=self.c.img_size_select), self.tag)
        movie.setField('backdrop_image', tmdbMovie.get_backdrop('s'), self.tag)
        movie.setField('overview', tmdbMovie.get_overview(), self.tag)
        movie.setField('runtime', tmdbMovie.get_runtime(), self.tag)
        movie.setField('id', tmdbMovie.get_id(), self.tag)
        movie.setField('id', tmdbMovie.get_imdb_id(), 'imdb')
        releaseDate = tmdbMovie.get_release_date()
        releaseDateTime = parse(releaseDate)

        movie.setField('release_date', releaseDateTime, self.tag)
        trailer_count = 0
        try:
            for index, youtubeTrailer in enumerate(tmdbMovie.get_trailers()['youtube']):
                trailerIDFieldName = 'youtube_trailer_id_%s' % index
                trailerNameFieldName = 'youtube_trailer_name_%s' % index
                movie.setField(trailerIDFieldName, youtubeTrailer['source'], self.tag)
                movie.setField(trailerNameFieldName, youtubeTrailer['name'], self.tag)
                trailer_count += 1
        except ValueError:
            pass

        movie.setField('tailer_count', trailer_count, self.tag)
        movie.saveTemp()

    def getElement(self, id, element=None):
        """we like tmdb ids"""
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.movies')
        mtm = common.PM.getMediaTypeManager('de.lad1337.movies')[0]
        fakeRoot = mtm.getFakeRoot('tmdb ID: %s' % id)
        tmdbMovie = tmdb.Movie(id)
        self._createMovie(fakeRoot, mediaType, tmdbMovie)

        for ele in fakeRoot.decendants:
            # print ele, ele.getField('id', self.tag)
            if str(ele.getField('id', self.tag)) == str(id):
                return ele
        else:
            return False

