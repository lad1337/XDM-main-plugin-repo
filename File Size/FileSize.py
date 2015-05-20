'''
Created on 25 Nov 2013

@author: unlord
'''

from xdm.plugins import DownloadFilter, log
import re


class FileSize(DownloadFilter):
    version = "0.1"
    identifier = 'de.lad1337.filesize'
    screenName = 'File Size'
    addMediaTypeOptions = 'runFor'
    _config = {'min_size': '',
               'max_size': ''}
    config_meta = {'plugin_desc': 'This plugin will filter out downloads by file size.', 
                   'min_size':{'human':'Minimum File Size', 'desc':'Written as e.g. 4 GB'},
                   'max_size':{'human':'Maximum File Size', 'desc':'Written as e.g. 4 GB'}}
    
    def _decodeSize(self, sizestr):
        match = re.search(r'(\d+(\.\d+)*)(\s*)([TGMK])B', sizestr)
        if match:
            size = float(match.group(1))
            if match.group(4) == "T":
                size = size * 1024 * 1024 * 1024
            elif match.group(4) == "G":
                size = size * 1024 * 1024
            elif match.group(4) == "M":
                size = size * 1024
            return int(size * 1024) #result in bytes
        else:
            log.error("Decoding torrent size from %s failed!" % sizestr)
        return 0

    @property
    def minimum(self):
        if self.c.min_size:
            return self._decodeSize(self.c.min_size)
        return 0

    @property
    def maximum(self):
        if self.c.max_size:
            return self._decodeSize(self.c.max_size)
        return 0

    def compare(self, element=None, download=None, string=None, forced=None):
        if download is None:
            return self.FilterResult(True, 'Can\'t filter a download if it doens\'t exist!')
        if not download.size:
            return self.FilterResult(True, 'Download has no size, can\'t filter!')
        if self.minimum and download.size<self.minimum:
            return self.FilterResult(False, '%i is smaller than %i' % (download.size, self.minimum))
        if self.maximum and download.size>self.maximum:
            return self.FilterResult(False, '%i is larger than %i' % (download.size, self.maximum))
        return self.FilterResult(True, 'Size is %i, between %i and %i, which is nice.' % (download.size, self.minimum, self.maximum))

