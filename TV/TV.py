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
import os

location = os.path.abspath(os.path.dirname(__file__))


class Episode(object):
    title = ''
    airdate = 0
    season = 0
    number = 0
    overview = ''
    screencap_image = ''

    _orderBy = 'number'
    _orderReverse = True

    def getTemplate(self):
        fp = os.path.join(location, "episode.ji2")
        with open (fp, "r") as template:
            return template.read()

    def getSearchTerms(self):
        return ['%s s%02de%02d' % (self.parent.parent.title, self.parent.number, self.number)]

    def getName(self):
        return "%se%02d %s" % (self.parent.getName(), self.number, self.title)

    def getReleaseDate(self):
        return self.airdate

    def getIdentifier(self):
        return self.number

class Season(object):
    number = 0
    poster_image = ''

    _orderBy = 'number'
    _orderReverse = True

    def getTemplate(self):
        fp = os.path.join(location, "season.ji2")
        with open (fp, "r") as template:
            return template.read()

    def getName(self):
        return "%s s%02d" % (self.parent.title, self.number)

    def getIdentifier(self):
        return self.number

class Show(object):
    title = ''
    id = ''
    airs = ''
    overview = ''
    year = 0
    poster_image = ''
    banner_image = ''
    fanart_image = ''
    show_status = ''
    country = ''
    genres = ''
    runtime = ''

    _orderBy = 'title'
    _orderReverse = True

    def getTemplate(self):
        fp = os.path.join(location, "show.ji2")
        with open (fp, "r") as template:
            return template.read()

    def getSearchTemplate(self):
        fp = os.path.join(location, "show_search.ji2")
        with open (fp, "r") as template:
            return template.read()

    def getName(self):
        return self.title

    def getIdentifier(self):
        return self.getField('id')

class TV(MediaTypeManager):
    version = "0.4"
    single = True
    _config = {'enabled': True}
    config_meta = {'plugin_desc': 'TV'}
    order = (Show, Season, Episode)
    download = Episode
    identifier = 'de.lad1337.tv'
    xdm_version = (0, 5, 9)
    addConfig = {}
    addConfig[Downloader] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'TV'}]
    addConfig[Indexer] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'TV'}]
    addConfig[PostProcessor] = [{'type':'path', 'default': None, 'prefix': 'Final path for', 'sufix': 'TV'}]

    def makeReal(self, show):
        show.parent = self.root
        show.status = common.getStatusByID(self.c.default_new_status_select)
        show.save()
        common.Q.put(('image.download', {'id': show.id}))
        for season in list(show.children):
            season.save()
            common.Q.put(('image.download', {'id': season.id}))
            for episode in list(season.children):
                episode.save()
                common.Q.put(('image.download', {'id': episode.id}))
        return True

    def headInject(self):
        return self._defaultHeadInject()

    def homeStatuses(self):
        return common.getEveryStatusBut([common.TEMP])

    def getUpdateableElements(self, asList=True):
        shows = Element.select().where(Element.type == 'Show',
                                       Element.parent == self.root)
        if asList:
            return list(shows)
        return shows

    def _episode_count(self, show, statuses=False):
        all_seasons = list(Element.select().where(Element.type == 'Season',
                                              Element.parent == show))
        seasons = [s for s in all_seasons if s.number]
        if statuses:
            return Element.select().where(Element.type == 'Episode',
                                          Element.parent << seasons,
                                          Element.status << statuses).count()
        else:
            return Element.select().where(Element.type == 'Episode',
                                          Element.parent << seasons).count()

    def _season_episode_count(self, season, statuses=False):
        if statuses:
            return Element.select().where(Element.type == 'Episode',
                                          Element.parent == season,
                                          Element.status << statuses).count()
        else:
            return Element.select().where(Element.type == 'Episode',
                                          Element.parent == season).count()
