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

import xdm
from xdm.plugins import *
import requests
from xdm import helper
import os
from urllib2 import urlopen, HTTPError
import time
import json
from distutils import dir_util
from glob import glob
import shutil
from xdm.tasks import TaskThread


class PMSDownloader(Downloader):
    version = "0.1"
    identifier = "de.lad1337.pms.downloader"
    types = ['de.lad1337.pms']
    addMediaTypeOptions = False
    config = {'tempoary_download_path': xdm.TEMPPATH,
               'final_download_path': os.path.expanduser("~/Download")}
    config_meta = {'plugin_desc': 'This will download the download link into a file. It can not check for the status of a download.'}

    def addDownload(self, download):
        tmp_dir = self.c.tempoary_download_path
        if not os.path.isdir(tmp_dir):
            log.info("Could not save %s at %s, it's not a valid folder" % (download, tmp_dir))
            return False
        songs = download.element.children

        this_tmp_dir = os.path.join(tmp_dir, self._downloadName(download))
        os.mkdir(this_tmp_dir)
        final_destination = os.path.join(self.c.final_download_path, self._downloadName(download))

        log.info(u"stating download thread on %s" % download)
        t = TaskThread(download_songs, this_tmp_dir, final_destination, songs, download.extra_data["songs"])
        t.start()
        return True

    def getElementStaus(self, element):
        """returns a Status and path"""
        download, path = self._scanFolder(self.c.tempoary_download_path, element)
        if download is not None:
            return (common.DOWNLOADING, download, path)

        download, path = self._scanFolder(self.c.final_download_path, element)
        if download is not None:
            return (common.DOWNLOADED, download, path)

        download = Download()
        download.status = common.UNKNOWN
        return (common.UNKNOWN, download, path)


    def _scanFolder(self, folder_path, element):
        download = None
        tmp_folder = ''
        for tmp_folder in glob(os.path.join(folder_path, "PMS *")):
            element_id = self._findElementID(tmp_folder)
            download_id = self._findDownloadID(tmp_folder)
            if element_id == element.id:
                break
        else:
            return (None, tmp_folder)
        try:
            download = Download.get(Download.id == download_id)
        except Download.DoesNotExist:
            pass
        return (download, tmp_folder)

def download_songs(this_tmp_dir, final_destination, songs, download_songs):
    for index, song in enumerate(download_songs):
        cur_song = songs[index]
        tmp_file_path = os.path.join(this_tmp_dir, u"{number} - {title}.mp3".format(number=cur_song.position, title=cur_song.title))
        mp3_location = download_song(tmp_file_path, song)
        log.info("file saved at %s" % mp3_location)
        log.debug("sleeping for 2sec")
        time.sleep(2)

    log.info("Download saved at %s moving to final folder %s" % (this_tmp_dir, final_destination))

    dir_util.copy_tree(this_tmp_dir, final_destination)
    shutil.rmtree(this_tmp_dir)
    log.info("Moved files")


# parts of pms where used to make this
"""
pms.

https://github.com/np1/pms

Copyright (C)  2013 nagev

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

def get_stream(song):
    """ Return the url for a song. """
    if not "track_url" in song:
        url = 'http://pleer.com/site_api/files/get_url?action=download&id=%s'
        url = url % song['link']
        try:
            log.debug("[0] fetching " + url)
            wdata = urlopen(url, timeout=30).read().decode("utf8")
            log.debug("fetched " + url)
        except Exception:
            time.sleep(2) # try again
            log.debug("[1] fetching 2nd attempt ")
            wdata = urlopen(url, timeout=7).read().decode("utf8")
            log.debug("fetched 2nd attempt" + url)

        j = json.loads(wdata)
        track_url = j['track_link']
        return track_url
    else:
        return song['track_url']

def download_song(destination, song):
    """ Download file, show status, return filename. """

    log.info("Downloading %s ..." % (destination))
    song['track_url'] = get_stream(song)
    log.debug("[4] fetching url " + song['track_url'])
    resp = urlopen(song['track_url'])
    log.debug("fetched url " + song['track_url'])
    chunksize = 16384
    outfh = open(destination, 'wb')

    while True:
        chunk = resp.read(chunksize)
        outfh.write(chunk)

        if not chunk:
            outfh.close()
            break


    return destination
