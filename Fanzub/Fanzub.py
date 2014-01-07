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
import requests
import re
import xml.etree.ElementTree as ET

class Fanzub(Indexer):
    version = "0.2"
    identifier = "de.lad1337.fanzub"
    types = ['de.lad1337.nzb']
    addMediaTypeOptions = "runFor"
    _config = {}
    config_meta = {'plugin_desc': 'Anime usenet indexer'}

    def searchForElement(self, element):
        if "anime" not in element.manager.identifier:
            return []

        payload = {"cat": "anime",
                   "max": 100
                   }
        downloads = []
        terms = element.getSearchTerms()
        for term in terms:
            payload['q'] = term
            r = requests.get("http://fanzub.com/rss", params=payload)
            log("Fanzub final search for term %s url %s" % (term, r.url))
            try:
                xml = ET.fromstring(r.text)
                items = xml.findall("channel/item")
            except Exception:
                log.exception(u"Error trying to load FANZUB RSS feed")
                continue

            for item in items:
                title = item.find("title").text
                if "- {:>02}".format(element.number) not in title:
                    continue
                url = item.find("link").text
                ex_id = re.search("/(\d+)", url).group(1)
                curSize = int(item.find("enclosure").attrib["length"])
                log("%s found on Fanzub: %s" % (element.type, title))
                d = Download()
                d.url = url
                d.name = title
                d.element = element
                d.size = curSize
                d.external_id = ex_id
                d.type = 'de.lad1337.nzb'
                downloads.append(d)

        return downloads
