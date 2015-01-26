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
    version = "0.6"
    identifier = "de.lad1337.xem.names"
    addMediaTypeOptions = 'runFor'

    _hidden_config = {
        'last_cache_tvdb': '',
        'last_cache_anidb': ''
    }
    def compare(self, element, terms):
        if element.type != "Episode":
            log("i only work for Episodes, i got a %s" % element.type)
            return terms

        new_names = []
        manager = element.manager
        if "tv" in manager.identifier:
            show = element.parent.parent
            new_names = self._build_terms_for_tv(
                element, self._names_for_show(show))
        if "anime" in manager.identifier:
            show = element.parent
            new_names = self._build_terms_for_anime(
                element, self._names_for_show(show))

        terms = new_names + terms
        return terms

    def _build_terms_for_anime(self, episode, names_data):
        new_terms = []
        for xem_name_data in names_data:
            for xem_name, season in xem_name_data.items():
                if season != -1:
                    continue
                new_terms.append(
                    "{show_name} {number:0>2}".format(
                        show_name=xem_name,
                        number=episode.number)
                )
        return new_terms

    def _build_terms_for_tv(self, episode, names_data):
        new_terms = []
        for xem_name_data in names_data:
            for xem_name, season in xem_name_data.items():
                if episode.parent.number == season or season == -1:
                    data = {"show_name": xem_name,
                            "s#": episode.parent.number,
                            "e#": episode.number
                            }
                    cur_name = u"{show_name} s{s#:0>2}e{e#:0>2}".format(**data)
                    new_terms.append(cur_name)
        return new_terms

    def _names_for_show(self, show):
        all_names = []
        for type in ("tvdb", "anidb"):
            orign_id = str(show.getField('id', type))
            log("{}_id for {} is {}".format(type, show, orign_id))
            if not orign_id:
                continue
            names = self._getNames(type)
            if orign_id in names:
                all_names += names[orign_id]
        return all_names

    def _getNames(self, origin, force=False):
        cache_file_path = os.path.join(my_install_folder, 'cache.{}.json'.format(origin))
        last_cache = getattr(self.hc, "last_cache_{}".format(origin))
        if (not last_cache or not os.path.isfile(cache_file_path) or parser.parse(last_cache) < datetime.now() - timedelta(days=1)) or force:
            log("getting new names from xem")
            params = {
                "origin": origin,
                "seasonNumbers": 1
            }
            r = requests.get("http://thexem.de/map/allNames", params=params)
            names = r.json()["data"]
            log("saving xem names to %s" % cache_file_path)
            with open(cache_file_path, "w") as cache:
                cache.write(json.dumps(names))
            setattr(
                self.hc, "last_cache_{}".format(origin), str(datetime.now()))


        with open(cache_file_path, "r") as cache:
            out = json.loads(cache.read())
        return out

    def _force_recache(self):
        name_data = self._getNames(True)
        return (True, {}, 'Recached {} show infos'.format(len(name_data)))
    _force_recache.args = []

    config_meta = {
        'plugin_desc': 'Gets additional names for TV shows from http://thexem.de',
        'plugin_buttons': {'force_recache': {'action': _force_recache, 'name': 'Force recache'}},
    }
