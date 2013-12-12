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
from xdm.helper import replaceUmlaute


class Song(object):
    position = 0
    title = ''
    lenght = 0.0

    _orderBy = 'position'

    def getTemplate(self):
        return '<li class="bORw"><span class="songPosition bORw">{{this.position}}</span><span class="songTitle bORw">{{this.title}}</span><span class="length bORw">{{this.length}}</span></li>'


class Album(object):
    name = ''
    year = 0
    cover_image = ''

    _orderBy = 'year'

    def getTemplate(self):
        return """<div class="Album {{statusCssClass}}" data-id="{{this.id}}">
                      <img src="{{this.cover_image}}">
                      <p>{{name}}<br><span class="artistName">{{this.parent.name}}</span></p>
                      <div class="indi">&#x25B2;</div>
                      <div class="songs">
                          <div class="info">
                              <strong class="bORw name">{{name}}</strong>{{actionButtons}}{{infoButtons}}{{statusSelect}}
                              <p class="bORw">{{this.parent.name}} ({{this.year}})</p>
                          </div>
                          <ol class="bORw"></ol>
                      </div>
                  </div>
                """

    def getSearchTerms(self):
        return ['%s %s' % (self.parent.name, self.name)]

    def getName(self):
        return self.name


class Artist(object):
    name = ''
    bio = ''

    _orderBy = 'name'

    def getName(self):
        return self.name

    def getTemplate(self):
        return '{{children}}'


class Music(MediaTypeManager):
    version = "0.5"
    xdm_version = (0, 5, 14)
    single = True
    _config = {'enabled': True}
    config_meta = {'plugin_desc': 'Music support. Good for Albums'}
    order = (Artist, Album, Song)
    download = Album
    identifier = 'de.lad1337.music'
    addConfig = {}
    addConfig[Downloader] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Music'}]
    addConfig[Indexer] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Music'}]
    addConfig[PostProcessor] = [{'type':'path', 'default': None, 'prefix': 'Final path for', 'sufix': 'Music'}]

    def makeReal(self, album, status):
        oldArtist = album.parent
        for artist in list(Element.select().where(Element.type == oldArtist.type,
                                             Element.mediaType == self.mt,
                                             Element.parent == self.root)):
            if artist.getField('id') == oldArtist.getField('id'):
                album.parent = artist
                album.status = status
                album.save()
                album.downloadImages()
                return True
        else:
            log('We dont have the artist so we copy that')
            newArtist = album.parent.copy()
            newArtist.parent = self.root
            newArtist.save()
            album.parent = newArtist
            album.status = status
            album.save()
            for song in list(album.children):
                song.save()
            album.downloadImages()
            return True

    def headInject(self):
        return self._defaultHeadInject()

