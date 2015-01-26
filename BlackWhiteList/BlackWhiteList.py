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
from collections import OrderedDict

class BlackWhiteList(DownloadFilter):
    version = "0.1"
    identifier = 'de.lad1337.blackwhitelist'
    screenName = 'BlackWhiteList'
    addMediaTypeOptions = 'runFor'

    elementConfig = OrderedDict([
        ('black_list', ''),
        ('black_list_any_all_select', 'any'),
        ('white_list', ''),
        ('white_list_any_all_select', 'any')
    ])

    config_meta = {
        'plugin_desc': 'Element specific black and white list filter.'
    }

    def compare(self, element=None, download=None, string=None, forced=False):
        self.e.getConfigsFor(element)
        if not self.e.black_list and not self.e.white_list:
            return self.FilterResult(True, "Nothing set... continue")

        blacks = [b for b in self.e.black_list.split(";") if b]
        if blacks:
            result = self._check_blacks(blacks, download.name)
            if result:
                return result

        whites = [w for w in self.e.white_list.split(";") if w]
        if whites:
            return self._check_whites(whites, download.name)

        return self.FilterResult(True, "Nothing set... continue")

    def _check_whites(self, whites, name):
        found_whites = [w for w in whites if w in name]
        if self.e.white_list_any_all_select == "any":
            if found_whites:
                return self.FilterResult(
                    True,
                    "Found at least one of white:'{}' in '{}'".format(
                        "', '".join(found_whites), name)
                )
        elif self.e.white_list_any_all_select == "all":
            if len(found_whites) == len(whites):
                return self.FilterResult(
                    True,
                    "Found all white:'{}' in '{}'".format(
                        "', '".join(found_whites), name)
                )
        return self.FilterResult(
            False, "Found not enough of white:'{}' in '{}'".format(
                found_whites, name))

    def _check_blacks(self, blacks, name):
        found_blacks = [b for b in blacks if b in name]
        if self.e.black_list_any_all_select == "any":
            if found_blacks:
                return self.FilterResult(
                    False,
                    "Found at least one black:'{}' in '{}'".format(
                        "', '".join(found_blacks), name)
                )
        elif self.e.black_list_any_all_select == "all":
            if len(found_blacks) == len(blacks):
                return self.FilterResult(
                    False,
                    "Found all black:'{}' in '{}'".format(
                        "', '".join(found_blacks), name)
                )

    def _black_list_any_all_select(self):
        return {"all": "All", "any": "At least one"}

    def _white_list_any_all_select(self):
        return {"all": "All", "any": "At least one"}
