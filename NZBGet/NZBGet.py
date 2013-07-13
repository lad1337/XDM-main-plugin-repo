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
from lib import requests

import xmlrpclib
from base64 import standard_b64encode


class NZBGet(Downloader):
    version = "0.2"
    identifier = "de.lad1337.nzbget"
    _config = {'port': 6789,
               'host': 'localhost',
               'user': 'nzbget',
               'password': '',
               'ssl': False}

    _history = []
    _queue = []
    types = ['de.lad1337.nzb']

    def _baseUrl(self, host, port, pw, user, ssl):
        # http://nzbget:yourpassword@localhost:6789/jsonrpc
        protocol = 'http'
        if ssl:
            protocol = 'https'
        return "%s://%s:%s@%s:%s/xmlrpc" % (protocol, user, pw, host, port)

    def addDownload(self, download):
        server = xmlrpclib.Server(self._baseUrl(self.c.host, self.c.port, self.c.password, self.c.user, self.c.ssl))
        server.writelog("INFO", "XDM connected to drop of %s any moment now." % download)
        log('Downloading nzb myself because that means we have more control.')

        r = requests.get(download.url)
        data = standard_b64encode(r.text)
        cat = self._getCategory(download.element)
        if not cat:
            cat = ''
        nzbgetResponse = server.append(self._downloadName(download) + ".nzb",
                                cat,
                                0,
                                False,
                                data)
        return nzbgetResponse

    def getDownloadPercentage(self, element):
        if not self._queue:
            self._getQueue()
        for i in self._queue:
            element_id = self._findElementID(i['NZBName'])
            if element_id != element.id:
                continue
            percentage = 100 - ((float(i['RemainingSizeMB']) / float(i['FileSizeMB'])) * 100)
            return percentage
        else:
            return 0

    def _getQueue(self):
        server = xmlrpclib.Server(self._baseUrl(self.c.host, self.c.port, self.c.password, self.c.user, self.c.ssl))
        self._queue = server.listgroups()
        return self._queue

    def _getHistory(self):
        server = xmlrpclib.Server(self._baseUrl(self.c.host, self.c.port, self.c.password, self.c.user, self.c.ssl))
        self._history = server.history()
        return self._history

    def getElementStaus(self, element):
        """returns a Status and path"""
        #log("Checking for status of %s in Sabnzbd" % element)
        download = Download()
        download.status = common.UNKNOWN
        if not self._history:
            self._getHistory()
        if not self._queue:
            self._getQueue()

        for curListNameKey, curList in (('NZBName', self._queue), ('Name', self._history)):
            for i in curList:
                element_id = self._findElementID(i[curListNameKey])
                download_id = self._findDownloadID(i[curListNameKey])
                if element_id != element.id:
                    continue
                try:
                    download = Download.get(Download.id == download_id)
                except Download.DoesNotExist:
                    pass
                if curListNameKey == 'NZBName': # if we found it in the queue we are downloading it !
                    return (common.DOWNLOADING, download, '')

                if curListNameKey == 'Name': # history
                    if i['UnpackStatus'] == 'SUCCESS' and i['ScriptStatus'] != 'FAILURE':
                        return (common.DOWNLOADED, download, i['DestDir'])
                    elif i['ParStatus'] == 'FAILURE' or i['ScriptStatus'] == 'FAILURE':
                        return (common.FAILED, download, '')
                    else:
                        return (common.SNATCHED, download, '')
        else:
            return (common.UNKNOWN, download, '')

    def _testConnection(self, host, port, password, user, ssl):
        url = self._baseUrl(host, port, password, user, ssl)
        server = xmlrpclib.Server(url)
        try:
            v = server.version()
        except:
            log.error('Some error while trying to connect to nzbget')
            return (False, {}, 'Some error while trying to connect to nzbget')
        return (True, {}, 'Connetion Established to NZBget v%s' % v)
    _testConnection.args = ['host', 'port', 'password', 'user', 'ssl']

    config_meta = {'plugin_desc': 'NZBGet downloader. Send NZBs and check for status',
                   'plugin_buttons': {'test_connection': {'action': _testConnection, 'name': 'Test connection'}},
                   'host': {'desc': 'Host without(!) the protocol scheme. NO http:// or http:// just localhost', 'on_live_change': _testConnection},
                   'port': {'on_live_change': _testConnection},
                   'ssl': {'human': 'SSL', 'desc': 'Sorry untested!', 'on_live_change': _testConnection},
                   'password': {'on_live_change': _testConnection}
                   }
