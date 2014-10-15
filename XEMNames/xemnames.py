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

import os
from xdm.plugins import *
from datetime import datetime, timedelta
import requests
import json
from dateutil import parser

my_install_folder = os.path.dirname(__file__)

class XEMNames(SearchTermFilter):
    version = "0.3"
    identifier = "de.lad1337.xem.names"
    addMediaTypeOptions = 'runFor'
    config_meta = {'plugin_desc': 'Gets additional names for TV shows from http://thexem.de',
                  }
    _hidden_config = {'last_cache': ''}
    def compare(self, element, terms):
        if element.type != "Episode":
            log("i only work for Episodes, i got a %s" % element.type)
            return terms
        show = element.parent.parent
        new_names = []
        for xem_name_data in self._names_for_show(show):
            for xem_name, season in xem_name_data.items():
                if element.parent.number == season or season == -1:
                    data = {"show_name": xem_name,
                            "s#": element.parent.number,
                            "e#": element.number
                            }
                    cur_name = u"{show_name} s{s#:0>2}e{e#:0>2}".format(**data)
                    new_names.append(cur_name)
        terms = new_names + terms
        return terms

    def _names_for_show(self, show):
        tvdb_id = str(show.getField('id', 'tvdb'))
        if not tvdb_id:
            log("no tvdb_id found for %s" % show)
            return []
        names = self._getNames()
        if tvdb_id in names:
            log("found the show by tvdb id on xem")
            return names[tvdb_id]
        else:
            return []


    def _getNames(self):
        cache_file_path = os.path.join(my_install_folder, 'cache.json')
        if not self.hc.last_cache or not os.path.isfile(cache_file_path) or parser.parse(self.hc.last_cache) < datetime.now() - timedelta(days=2):
            log("getting new names from xem")
            r = requests.get("http://thexem.de/map/allNames?origin=tvdb&seasonNumbers=1")
            names = r.json()["data"]
            log("saving xem names to %s" % cache_file_path)
            with open(cache_file_path, "w") as cache:
                cache.write(json.dumps(names))
            self.hc.last_cache = str(datetime.now())

        with open(os.path.join(my_install_folder, 'cache.json'), "r") as cache:
            out = json.loads(cache.read())
        return out
