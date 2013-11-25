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

# all xdm related plugin stuff you get with this line incl logger functions
from xdm.plugins import *
# other libs should be imported as you need them but why dont you have a look at the libs xdm comes with
from lib import requests
from xdm import helper
import os, re


class Blackhole(Downloader):
    version = "0.6"
    identifier = "de.lad1337.blackhole"
    types = []
    _config = {'monitor_path':'',
               'search_threshold':0.75}
    config_meta = {'plugin_desc': 'This will download the download link into a file. It can not check the progress of a download, only whether it is finished or not.', 
                   'monitor_path':{'human':'Finished Downloads will be at', 'desc':'The path where Blackhole will be searching for finished downloads'},
                   'search_threshold':{'human':'Search Threshold for Finished Downloads', 'desc':'a number between 0.0 and 1.0 indicating how well a found file name must match the download filename to trigger a finished download'}}
    useConfigsForElementsAs = 'Path'
    
    def addDownload(self, download):
        b_dir = self._getPath(download.element)
        if not os.path.isdir(b_dir):
            log.info("Could not save %s at %s, it's not a valid folder" % (download, b_dir))
            return False

        file_name = '%s.%s' % (self._downloadName(download), self._getDownloadTypeExtension(download.type))
        dst = os.path.join(b_dir, helper.fileNameClean(file_name))
        headers = download.extra_data['headers'] if 'headers' in download.extra_data else { }
        r = requests.get(download.url, headers=headers)
        if r.status_code == 200:
            with open(dst, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        else:
            log.info("Download save to Blackhole at %s failed" % dst)
            return False

        log.info("Download saved to Blackhole at %s" % dst)
        return True
    
    def _ratePath(self, filename, snatched):
        file_parts = set([p.lower() for p in re.split(r'\W',filename)])
        for s in snatched:
            name_parts = set([p.lower() for p in re.split(r'\W',s.name)])
            inter = name_parts.intersection(file_parts)
            dice = 2.0*len(inter)/(len(name_parts)+len(file_parts))
            log.debug('BlackHole: DICE for %s and %s is %.03f' % (filename, s.name, dice))
            yield (s, dice)
    
    def _ratePaths(self, base, snatched):
        log.debug("BlackHole rating paths in %s" % (base))
        for dirpath, dirnames, filenames in os.walk(base):
            for f in filenames:
                for r in self._ratePath(f, snatched):
                    yield (dirpath, f, r[0], r[1])
    
    def getElementStaus(self, element):
        snatched = [d for d in element.downloads if d.status == common.SNATCHED]
        rated_paths = sorted(self._ratePaths(self.c.monitor_path, snatched), key=lambda x:x[-1], reverse=True)
        if len(rated_paths) > 0:
            if rated_paths[0][3]>self.c.search_threshold:
                if rated_paths[0][0] == self.c.monitor_path:
                    return (common.DOWNLOADED, rated_paths[0][2], os.path.join(rated_paths[0][0], rated_paths[0][1]))
                else:
                    return (common.DOWNLOADED, rated_paths[0][2], rated_paths[0][0])
        return (common.UNKNOWN, Download(), '')

