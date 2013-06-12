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
import re


class Book(object):
    title = ''
    author = ''
    cover_image = ''

    _orderBy = ('author', 'title')

    def getTemplate(self):
        return """
        <div class="{{statusCssClass}}">
            <img src="{{this.cover_image}}" class="pull-left"/>
            <span class="pull-left">
                <br/>
                <span>{{this.author}}</span>
                <strong>{{this.title}}</strong><br/>
                <br/>
                <span>
                    {{actionButtons}}
                    {{infoButtons}}
                    {{statusSelect}}
                    {{downloadProgressBar}}
                </span>
            </span>
            <div class="clearfix"></div>
        </div>
        """

    def getSearchTerms(self):
        fullName = self.getName()
        # removing stuff like (Book Name, #3)
        stripped = re.sub(r'\(.*?#\d+\)$', '', fullName)
        return [stripped]

    def getName(self):
        return '%s %s' % (self.author, self.title)


class Books(MediaTypeManager):
    version = "0.1"
    xdm_version = (0, 4, 17) # this is the greater or equal xdm version it needs
    # we need version 0.4.16 because _oderBy with multiple indexes was introduced
    _config = {}
    config_meta = {'plugin_desc': "Simple Books. Needs Core version 0.4.17 and version checking was only implemented in 0.4.16 so don't install if you don't have anything like that."}
    order = (Book,)
    download = Book
    # a unique identifier for this mediatype
    identifier = 'de.lad1337.books'
    addConfig = {}
    addConfig[Indexer] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Books'}]
    addConfig[Downloader] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Books'}]

    def makeReal(self, book):
        book.parent = self.root
        book.status = common.getStatusByID(self.c.default_new_status_select)
        book.save()
        book.downloadImages()
        return True




