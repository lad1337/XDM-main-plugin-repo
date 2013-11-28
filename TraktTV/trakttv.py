# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://github.com/lad1337/XDM
#
# This file is part of XDM: eXtentable Download Manager.
#
#XDM: eXtentable Download Manager. Plugin based media collection manager.
#Copyright (C) 2013  Dennis Lutter
#
#XDM is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#XDM is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see http://www.gnu.org/licenses/.

from xdm.plugins import *
import datetime
from lib import dateutil

import trakt.tv

class TraktTV(Provider):
    version = "0.2"
    identifier = "de.lad1337.trakt.tv"
    _tag = 'trakt'
    _additional_tags = ['tvdb']
    single = True
    types = ['de.lad1337.tv']
    _config = {'api_key': ''}
    config_meta = {'plugin_desc': 'TV show info from http://trakt.tv. Get your api key from http://trakt.tv/settings/api'}

    def __init__(self, instance='Default'):
        Provider.__init__(self, instance=instance)
        trakt.tv.setup(apikey=self.c.api_key)

    def searchForElement(self, term=''):

        self.progress.reset()
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = common.PM.getMediaTypeManager('de.lad1337.tv')[0]
        fakeRoot = mtm.getFakeRoot(term)

        log('trakt.tv searching for %s' % term)

        _results = trakt.tv.search.shows(term)
        self.progress.total = len(_results)
        for _show in _results:
            _show = trakt.tv.show.summary(_show['tvdb_id'], True)
            self.progress.addItem()
            self._build_show(_show, fakeRoot, mediaType)

        return fakeRoot

    def _build_show(self, _show, fakeRoot, mediaType):
        show = Element()
        show.mediaType = mediaType
        show.parent = fakeRoot
        show.type = 'Show'
        show.setField('title', _show['title'], self.tag)
        show.setField('overview', _show['overview'], self.tag)
        show.setField('year', _show['year'], self.tag)
        show.setField('show_status', _show['status'], self.tag)
        show.setField('country', _show['country'], self.tag)
        show.setField('genres', ', '.join(_show['genres']), self.tag)
        show.setField('runtime', _show['runtime'], self.tag)
        show.setField('poster_image', _show['images']['poster'], self.tag)
        show.setField('banner_image', _show['images']['banner'], self.tag)
        show.setField('fanart_image', _show['images']['fanart'], self.tag)
        show.setField('id', _show['tvdb_id'], "tvdb")
        show.saveTemp()
        for _simple_season in _show['seasons']:
            season = Element()
            season.mediaType = mediaType
            season.parent = show
            season.type = 'Season'
            season.setField('number', _simple_season['season'], self.tag)
            season.setField('poster_image', _simple_season['images']['poster'], self.tag)
            season.saveTemp()
            for _episode in _simple_season['episodes']:
                episode = Element()
                episode.mediaType = mediaType
                episode.parent = season
                episode.type = 'Episode'
                episode.setField('title', _episode['title'], self.tag)
                episode.setField('season', _episode['season'], self.tag)
                episode.setField('number', _episode['episode'], self.tag)
                episode.setField('overview', _episode['overview'], self.tag)
                episode.setField('id', _episode['tvdb_id'], "tvdb")
                if _episode['first_aired_iso']:
                    airdate = dateutil.parser.parse(_episode['first_aired_iso'])
                    episode.setField('airdate', airdate, self.tag)
                else:
                    episode.setField('airdate', common.FAKEDATE, self.tag)
                episode.setField('screencap_image', _episode['images']['screen'], self.tag)
                episode.saveTemp()


    def getElement(self, id, element=None):
        tvdb_id = element.getField('id', 'tvdb')
        
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = common.PM.getMediaTypeManager('de.lad1337.tv')[0]
        fakeRoot = mtm.getFakeRoot(tvdb_id)
        
        _show = trakt.tv.show.summary(tvdb_id, True)
        self._build_show(_show, fakeRoot, mediaType)
    
        for ele in fakeRoot.decendants + [_show]:
            if element is not None:
                if ele.getField('id', 'tvdb') == id:
                    return ele
                
        return False
    
    
