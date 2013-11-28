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
import time
import fnmatch
import re
import shutil
import os
import errno

# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class EpisodeMover(PostProcessor):
    identifier = 'de.lad1337.tv.simplemover'
    version = "0.1"
    types = ["de.lad1337.tv"]
    _config = {'show_parent_path': "",
               'name_format': '{show_name}/{s#}/{show_name} - s{s#}e{e#} - {title}',
               }
    screenName = 'Episode Mover'
    addMediaTypeOptions = False
    config_meta = {'plugin_desc': 'This will move the episode based on a format string.',
                   'name_format': {'desc': '{show_name}: the show name, {s#}: season number, {s#}: episode number, {title}: episode title'}
                   }

    _allowed_extensions = ('.avi', '.mkv', '.iso', '.mp4')

    def postProcessPath(self, element, filePath):
        if not self.c.show_parent_path:
            msg = "Destination path for %s is not set. Stopping PP." % element
            log.warning(msg)
            return (False, msg)
        # log of the whole process routine from here on except debug
        # this looks hacky: http://stackoverflow.com/questions/7935966/python-overwriting-variables-in-nested-functions
        processLog = [""]

        def processLogger(message):
            log.info(message)
            createdDate = time.strftime("%a %d %b %Y / %X", time.localtime()) + ": "
            processLog[0] = processLog[0] + createdDate + message + "\n"

        def fixName(name):
            return name.replace(":", " ")

        allEpisodeFileLocations = []
        if os.path.isdir(filePath):
            processLogger("Starting file scan on %s" % filePath)
            for root, dirnames, filenames in os.walk(filePath):
                processLogger("I can see the files %s" % filenames)
                for filename in filenames:
                    if filename.endswith(self._allowed_extensions):
                        if 'sample' in filename.lower():
                            continue
                        curFile = os.path.join(root, filename)
                        allEpisodeFileLocations.append(curFile)
                        processLogger("Found episode: %s" % curFile)
            if not allEpisodeFileLocations:
                processLogger("No files found!")
                return (False, processLog[0])
        else:
            allEpisodeFileLocations = [filePath]

        if allEpisodeFileLocations > 1:
            processLogger("Sorry i found more then one file i don't know what to do...")
            return (False, processLog[0])

        processLogger("Renaming and moving episode")
        success = True

        curFile = allEpisodeFileLocations[0]
        processLogger("Processing episode: %s" % curFile)
        try:
            extension = os.path.splitext(curFile)[1]
            newFileRoute = u"%s%s" % (self._build_file_name, extension)
            processLogger("New Filename shall be: %s" % newFileRoute)

            dst = os.path.join(self.c.show_parent_path, newFileRoute)
            processLogger("Creating folders leading to %s" % dst)
            mkdir_p(os.path.dirname(dst))
            processLogger("Moving File from: %s to: %s" % (curFile, dst))
            shutil.move(curFile, dst)
        except Exception, msg:
            processLogger("Unable to rename and move episode: %s. Please process manually" % curFile)
            processLogger("given ERROR: %s" % msg)
            success = False

        processLogger("File processing done")
        # write process log
        logFileName = helper.fileNameClean(u"%s.log" % element.getName())
        logFilePath = os.path.join(filePath, logFileName)
        try:
            # This tries to open an existing file but creates a new file if necessary.
            logfile = open(logFilePath, "a")
            try:
                logfile.write(processLog[0])
            finally:
                logfile.close()
        except IOError:
            pass

        return (success, processLog[0])

    def _build_file_name(self, element):
        return element.getName()
        # '{show_name}/{s#}/{show_name} - s{s#}e{e#} - {title}'
        map = {"show_name": element.parent.parent.title,
               "title": element.title,
               "s#": element.parent.number,
               "e#": element.number,
               }
        name = self.c.name_format.format(**map)
        log.debug("build the name: %s with %s" % (name, map))
        return name


