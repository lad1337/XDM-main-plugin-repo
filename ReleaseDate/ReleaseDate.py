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

from xdm.plugins import *
from xdm import helper
from babel.dates import format_timedelta
from datetime import datetime, timedelta


class ReleaseDate(DownloadFilter):
    version = "0.1"
    identifier = 'de.lad1337.filter.releasedate'
    screenName = 'Release Date'
    addMediaTypeOptions = 'runFor'
    stages = [DownloadFilter._pre_search]
    _config = {'release_threshold_select': '', }

    config_meta = {'release_threshold_select': {'human': 'Time to ignore the release date prior the release date.'}}

    elementConfig = {'format_select': 'format_select',
                     'screenSize_select': 'screenSize_select',
                     'audioCodec_select': 'audioCodec_select',
                     'any_all_select': 'any_all_select'}


    _releaseThresholdDelta = {1: timedelta(days=1),
                              2: timedelta(days=2),
                              3: timedelta(days=7), # a week
                              4: timedelta(days=30), # a month
                              5: timedelta(days=60)} # two months

    def compare(self, element=None, download=None, string=None, forced=False):
        if self.c.skip_on_forced_search and forced:
            self.FilterResult(True, 'Skipping: foced search')

        self.e.getConfigsFor(element) # this will load all the elements configs
        # into the the self.e cache
        # needed for .<config_name_access>
        thresholdRD = self._releaseThresholdDelta[self.c.release_threshold_select]
        if (element.getReleaseDate() - thresholdRD) > datetime.datetime.now():
            return self.FilterResult(False, 'To early to search for %s' % element)

        return self.FilterResult(True, 'Release date of %s is in the threshold' % element)

    def _release_threshold_select(self):
        _local = common.getLocale()
        return {0: "Don't ignore.",
                1: format_timedelta(self._releaseThresholdDelta[1], locale=_local),
                2: format_timedelta(self._releaseThresholdDelta[2], locale=_local),
                3: format_timedelta(self._releaseThresholdDelta[3], locale=_local),
                4: format_timedelta(self._releaseThresholdDelta[4], locale=_local),
                5: format_timedelta(self._releaseThresholdDelta[5], locale=_local),
                6: 'Completely ignore'}
