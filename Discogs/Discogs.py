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

import discogs_client
import re

user_agent = '%s +http://xdm.lad1337.de' % common.getVersionHuman()


OAuth = common.PM.getPluginByIdentifier("de.lad1337.oauth").OAuth1

class Discogs(Provider):
    xdm_version = (99, 99, 99)
    version = "0.13"
    identifier = "de.lad1337.music.discogs"
    _tag = 'discogs'
    single = True
    types = ['de.lad1337.music']
    _config = {'enabled': True,
               'search_range_select': 'master'}
    config_meta = {'plugin_desc': 'Information provider for music from http://www.discogs.com. Note: Image download is limited to 1000 per 24h per IP'
                   }

    search_range_select_map = {'master': {'t': 'Master Releases', 'c': ('MasterRelease',)},
                               'both': {'t': 'Master & Normal Releases', 'c': ('MasterRelease', 'Release')},
                               'releases': {'t': 'Releases', 'c': ('Release',)}}

    oauth = OAuth(
        "mjdbIivOosoimlstofrw",
        "rspGOethLnnrIBLoLijcmiRmaMXirugB",
        request_token_url="https://api.discogs.com/oauth/request_token",
        authorize_url="https://www.discogs.com/oauth/authorize",
        token_url="https://api.discogs.com/oauth/access_token",
        headers={"User-Agent": user_agent}
    )

    def __init__(self, instance):
        super(Discogs, self).__init__(instance)
        # https://github.com/discogs/discogs_client
        self.d = discogs_client.Client(
            user_agent,
            consumer_key=self.oauth.consumer_key,
            consumer_secret=self.oauth.consumer_secret,
            token=self.oauth.resource_owner_key,
            secret=self.oauth.resource_owner_secret
        )

    def _search_range_select(self):
        out = {}
        for i, o in self.search_range_select_map.items():
            out[i] = o['t']
        return out

    def searchForElement(self, term=''):

        self.progress.reset()
        # artist = discogs.Artist('Aphex Twin')
        mediatype = MediaType.get(MediaType.identifier == 'de.lad1337.music')
        mtm = common.PM.getMediaTypeManager('de.lad1337.music')[0]


        results = self.d.search(term, type='release')

        fakeRoot = mtm.getFakeRoot(term)

        self.progress.total = 10

        for index, release in enumerate(results):
            self.progress.addItem()
            self._createAlbum(fakeRoot, mediatype, release)
            if index >= 10:
                break
        return fakeRoot

    def _createAlbum(self, fakeRoot, mediaType, release):

        artist = release.artists[0]
        artistName = re.sub(r' \(\d{1,2}\)$', '', artist.name)
        try:
            artistElement = Element.getWhereField(mediaType, 'Artist', {'id': artistName}, self.tag, fakeRoot)
        except Element.DoesNotExist:
            artistElement = Element()
            artistElement.mediaType = mediaType
            artistElement.parent = fakeRoot
            artistElement.type = 'Artist'
            artistElement.setField('name', artistName, self.tag)
            artistElement.setField('id', artistName, self.tag)
            artistElement.saveTemp()
        try:
            albumElement = Element.getWhereField(mediaType, 'Album', {'id': release.data['id']}, self.tag, artistElement)
            print "we have", albumElement
        except Element.DoesNotExist:
            albumElement = Element()
            albumElement.mediaType = mediaType
            albumElement.parent = artistElement
            albumElement.type = 'Album'
            albumElement.setField('name', release.title, self.tag)
            albumElement.setField('year', release.data['year'], self.tag)
            albumElement.setField('id', release.data['id'], self.tag)
            if 'images' in release.data:
                for img in release.data['images']:
                    if img['uri']:
                        albumElement.setField('cover_image', img['uri'], self.tag)
                        break
            albumElement.saveTemp()
            for track in release.tracklist:
                trackElement = Element()
                trackElement.mediaType = mediaType
                trackElement.parent = albumElement
                trackElement.type = 'Song'
                trackElement.setField('title', track.title, self.tag)
                trackElement.setField('length', track.duration, self.tag)
                trackElement.setField('position', track.position, self.tag)
                trackElement.saveTemp()
            albumElement.downloadImages()

    def getElement(self, id, element=None, tag=None):
        mt = MediaType.get(MediaType.identifier == 'de.lad1337.music')
        mtm = common.PM.getMediaTypeManager('de.lad1337.music')[0]
        fakeRoot = mtm.getFakeRoot('%s ID: %s' % (self.tag, id))
        release = self.d.release(id)
        master = self.d.master(id)
        # print release
        # print master
        for release_type in (master, release):
            try:
                self._createAlbum(fakeRoot, mt, release_type)
            except AttributeError:
                pass

        for ele in fakeRoot.decendants:
            if element is None:
                if ele.getField('id', self.tag) == id:
                    return ele
            else:
                """print ele.getField('id', self.tag), id, ele.getField('id', self.tag) == id
                print element.type, ele.type, element.type == ele.type
                print element.parent.getField('id', self.tag), ele.parent.getField('id', self.tag), element.parent.getField('id', self.tag) == ele.parent.getField('id', self.tag)
                print '#############'"""
                if ele.getField('id', self.tag) == id and element.type == ele.type and element.parent.getField('id', self.tag) == ele.parent.getField('id', self.tag):
                    return ele
        else:
            return False
