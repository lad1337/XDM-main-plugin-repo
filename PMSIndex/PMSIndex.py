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
import requests
from xdm import helper
import re
import time
from urllib2 import urlopen, URLError, HTTPError
from uuid import uuid4
import difflib


class PMSIndex(Indexer):
    version = "0.1"
    identifier = "de.lad1337.pms.index"
    addMediaTypeOptions = ['de.lad1337.music']
    _config = {}
    config_meta = {'plugin_desc': 'Generic Newznab indexer. Categories are there numerical id of Newznab, use "Get categories"'}
    types = ['de.lad1337.pms']

    def searchForElement(self, element):
        songs = element.children

        found_songs = []
        bitrates = []
        complete_size = 0

        for song in songs:
            song_versions = dosearch(u"{} {}".format(element.parent.name, song.title))
            best_song = None
            best_song_score = (0, 0, 0)
            log(u"found %d versions for %s - %s" % (len(song_versions), element.parent.name, song.title))
            for song_version in song_versions:
                distance = difflib.SequenceMatcher(None, element.parent.name, song_version["singer"]).ratio()
                rate = song_version["rate_int"]
                size = song_version["size"]
                print song_version, (distance, size, rate), best_song_score
                if (distance, size, rate) > best_song_score:
                    best_song_score = (distance, size, rate)
                    best_song = song_version
            if best_song:
                log.info(u"choose %s for %s with score %s" % (best_song, song.title, best_song_score))
                found_songs.append(best_song)
                complete_size += best_song["size"]
                bitrates.append(best_song["rate_int"])
            else:
                log.info("could not find a result for %s i am done here." % song)
                return []
        if not found_songs:
            return []

        d = Download()
        d.url = str(uuid4())
        d.name = "%d songs an average bitrate of %s" % (len(found_songs), sum(bitrates) / len(bitrates))
        d.element = element
        d.size = complete_size
        d.external_id = str(uuid4())
        d.type = 'de.lad1337.pms'
        d.extra_data["songs"] = found_songs

        return [d]

    def commentOnDownload(self, msg, download):
        return True


class PMS(DownloadType):
    version = "0.1"
    identifier = 'de.lad1337.pms'
    extension = 'mp3'
    _config = {'enabled': True}
    config_meta = {'plugin_desc': 'NZB / Usenet download type.'}


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

def dosearch(term):
    """ Perform search. """
    url = "http://pleer.com/search?q=%s&target=tracks&page=%s"
    url = url % (term.replace(" ", "+"), 1)
    try:
        log.debug("[3] fetching " + url)
        wdata = requests.get(url)
        songs = get_tracks_from_page(wdata.text)
        if songs:
            return songs
        else:
            return []
    except Exception:
        log.error("HTTP Error fetching url:" + url)
        return []


def get_tracks_from_page(page):
    """ Get search results from web page. """
    fields = "duration file_id singer song link rate size source".split()
    matches = re.findall(r"\<li.(duration[^>]+)\>", page)
    songs = []
    if matches:
        for song in matches:
            cursong = {}
            for f in fields:
                v = re.search(r'%s=\"([^"]+)"' % f, song)
                if v:
                    cursong[f] = tidy(v.group(1), f)
                    cursong["R" + f] = v.group(1)
                else:
                    break
            else:
                try:
                    cursong = get_average_bitrate(cursong)
                except ValueError: # cant convert rate to int: invalid literal for int() with base 10: '96 K'
                    continue
                # u'4.514 Mb'
                cursong['size'] = int(float(cursong['size'][:3]) * 1024.0 * 1024.0)
                songs.append(cursong)
                continue

    else:
        log.debug("got unexpected webpage or no search results")
        return False
    return songs

def get_average_bitrate(song):
    """ calculate average bitrate of VBR tracks. """
    if song["rate"] == "VBR":
        vbrsize = float(song["Rsize"][:-3]) * 10000
        vbrlen = float(song["Rduration"])
        vbrabr = str(int(vbrsize / vbrlen))
        song["listrate"] = vbrabr + " v" # for display in list
        song["rate"] = vbrabr + " Kb/s VBR" # for playback display
    else:
        song["listrate"] = song["rate"][:3] # not vbr list display
    song["rate_int"] = int(song["rate"][:4])

    return song

def tidy(raw, field):
    """ Tidy HTML entities, format songlength if field is duration.  """
    if field == "duration":
        raw = time.strftime('%M:%S', time.gmtime(int(raw)))
    else:
        for r in (("&#039;", "'"), ("&amp;#039;", "'"), ("&amp;amp;", "&"),
                 ("  ", " "), ("&amp;", "&"), ("&quot;", '"')):
            raw = raw.replace(r[0], r[1])
    return raw
