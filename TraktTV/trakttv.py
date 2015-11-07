# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://github.com/lad1337/XDM-main-plugin-repo/
#
# This file is part of a XDM plugin.
#
# XDM plugin.
# Copyright (C) 2013  Dennis Lutter
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from xdm.plugins import *
import datetime
from dateutil import parser

from easytrakt import Client
from easytrakt.models import Show

OAuth = common.PM.getPluginByIdentifier("de.lad1337.oauth").OAuth2

base_url = "https://api.trakt.tv"

class TraktTV(Provider):
    version = "0.10"
    identifier = "de.lad1337.trakt.tv"
    _tag = 'trakt'
    single = True
    types = ['de.lad1337.tv']
    _config = {
        'api_key': '',
        'release_delta': 0,
    }
    config_meta = {
        'plugin_desc':'TV show info from http://trakt.tv.',
        'release_delta': {'human': 'Timedelta for the air time in hours', 'desc': 'e.g. -8 or 12'}
    }

    oauth = OAuth(
        "f0fe381da214b07add42d10875548f2e589d96ed442f740ce56c286f66a3c8e6",
        "915a1f80a7ba4fb55e889067f7a819835b522d0b5ff9b5e42b2e5653d65c3946",
        authorization_url="https://trakt.tv/oauth/authorize",
        token_url="https://api.trakt.tv/oauth/token"
    )

    def __init__(self, instance='Default'):
        Provider.__init__(self, instance=instance)
        self.client = Client()
        if self.oauth.authorized:
            self.client = Client(self.oauth.session)

    def searchForElement(self, term=''):
        self.progress.reset()
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = common.PM.getMediaTypeManager('de.lad1337.tv')[0]
        fakeRoot = mtm.getFakeRoot(term)


        log('trakt.tv searching for %s' % term)

        _results = self.client.shows(term)
        self.progress.total = len(_results)
        for _show in _results:
            self.progress.addItem()
            self._build_show(_show, fakeRoot, mediaType, just_show=True)

        return fakeRoot

    def _build_show(self, show_, fakeRoot, mediaType, just_show=False):
        show = Element()
        show.mediaType = mediaType
        show.parent = fakeRoot
        show.type = 'Show'
        show.setField('title', show_.title, self.tag)
        show.setField('overview', show_.overview, self.tag)
        show.setField('year', show_.year, self.tag)
        show.setField('show_status', show_.status, self.tag)
        show.setField('country', show_.country, self.tag)
        show.setField('genres', ', '.join(show_.genres), self.tag)
        show.setField('runtime', show_.runtime, self.tag)
        show.setField('poster_image', show_.images.poster.medium, self.tag)
        show.setField('banner_image', show_.images.banner.full, self.tag)
        show.setField('fanart_image', show_.images.fanart.medium, self.tag)
        for id_key in ["tvdb", "imdb", "trakt"]:
            id_ = getattr(show_.ids, id_key)
            if id_:
                show.setField('id', id_, id_key)
        show.saveTemp()
        if just_show:
            return

        for season_ in show_.seasons:
            season = Element()
            season.mediaType = mediaType
            season.parent = show
            season.type = 'Season'
            season.setField('number', season_.number, self.tag)
            season.setField('poster_image', season_.images.poster.medium, self.tag)
            season.saveTemp()
            for episode_ in season_.episodes:
                episode = Element()
                episode.mediaType = mediaType
                episode.parent = season
                episode.type = 'Episode'
                episode.setField('title', episode_.title, self.tag)
                episode.setField('season', episode_.season, self.tag)
                episode.setField('number', episode_.number, self.tag)
                episode.setField('overview', episode_.overview, self.tag)
                episode.setField('id', episode_.ids.tvdb, "tvdb")
                if episode_.first_aired:
                    episode.setField('airdate', episode_.first_aired, self.tag)
                else:
                    episode.setField('airdate', common.FAKEDATE, self.tag)
                episode.setField(
                    'screencap_image', episode_.images.screenshot.medium, self.tag)
                episode.saveTemp()


    def getElement(self, show_id, element=None, tag=None):
        mediaType = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = common.PM.getMediaTypeManager('de.lad1337.tv')[0]
        fakeRoot = mtm.getFakeRoot(show_id)

        show = Show(self.client, show_id) # only supports trakt id
        log("building show: %s" % show)
        self._build_show(show, fakeRoot, mediaType)

        for ele in fakeRoot.decendants:
            if int(ele.getField('id', tag)) == int(show_id):
                return ele
        return False


