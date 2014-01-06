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
import re


def _getNormalTemplate():
    return """
    <div class="{{statusCssClass}} book-container well">
        <img src="{{this.cover_image}}" class="pull-left"/>
        <div class="pull-left">
            <h4>{{this.title}}</h4>
            <h5>{{this.author}}</h5>
            <p><span>Rating: {{this.rating}}</span></p>
            {{statusSelect}}{{actionButtons}}{{infoButtons}}
        </div>
        <div class="clearfix"></div>
    </div>
    """


def _getFancyTemplate(bookID):
    mod = bookID % 10
    if not mod:
        mod = 10
    spine = '{{myUrl}}/images/book_%s.png' % mod

    return """
    <div class="{{statusCssClass}} book" data-toggle="tooltip" title="{{this.title}} - {{this.author}}"  data-placement="bottom">
        <img src="%s" class="spine"/>
        <img src="{{myUrl}}/images/paper_side.png" class="side"/>
        <img src="{{myUrl}}/images/book_back.png" class="back"/>
        <div class="inner">
            <img src="{{this.cover_image}}"/>
            <div class="paper">
                <h4>{{this.title}}</h4>
                <h5>{{this.author}}</h5>
                <div class="clearfix"></div>
                <span>Rating: {{this.rating}}</span>
                <p>
                {{statusSelect}}
                </p>
                <p>
                {{actionButtons}}
                </p>
                <p>
                {{infoButtons}}
                </p>
            </div>
        </div>
    </div>
    """ % spine


class Book(object):
    title = ''
    author = ''
    cover_image = ''
    rating = ''

    _orderBy = ('author', 'title')

    def getTemplate(self):
        if self.manager.c.gui_select == "fancy":
            return _getFancyTemplate(self.id)
        return _getNormalTemplate()

    def getSearchTerms(self):
        fullName = self.getName()
        # removing stuff like (Book Name, #3)
        stripped = re.sub(r'\(.*?#\d+\)$', '', fullName)
        return [stripped]

    def getName(self):
        return '%s %s' % (self.author, self.title)


class Books(MediaTypeManager):
    version = "0.8"
    xdm_version = (0, 5, 14) # this is the greater or equal xdm version it needs
    # we need version 0.4.16 because _oderBy with multiple indexes was introduced
    _config = {"gui_select": "normal"}
    config_meta = {'plugin_desc': "Simple Books with two GUIs."}
    order = (Book,)
    download = Book
    # a unique identifier for this mediatype
    identifier = 'de.lad1337.books'
    addConfig = {}
    addConfig[Indexer] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Books'}]
    addConfig[Downloader] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Books'}]

    def _gui_select(self):
        return {"normal": "Normal",
                "fancy": "Fancy"}

    def makeReal(self, book, status):
        book.parent = self.root
        book.status = status
        book.save()
        book.downloadImages()
        return True

    def headInject(self):
        return self._defaultHeadInject()

