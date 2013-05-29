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
from xdm import helper
import time
import fnmatch
import os
import re
import shutil


class MovieMover(PostProcessor):
    identifier = 'de.lad1337.movie.simplemover'
    version = "0.14"
    _config = {"replace_space_with": " ",
               'final_movie_path': ""
               }
    screenName = 'Movie Mover'
    addMediaTypeOptions = ['de.lad1337.movies']
    config_meta = {'plugin_desc': 'This will move all the avi, mkv, iso, mp4 from the path that is given to the path.',
                   'replace_space_with': {'desc': 'All spaces for the final file will be replaced with this.'}
                   }
    useConfigsForElementsAs = 'Path'

    def postProcessPath(self, element, filePath):
        destPath = self.c.final_movie_path
        if not destPath:
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

        def fixName(name, replaceSpace):
            return helper.fileNameClean(name.replace(" ", replaceSpace))

        allMovieFileLocations = []
        if os.path.isdir(filePath):
            processLogger("Starting file scan on %s" % filePath)
            # gather all images -> .iso and .img
            for root, dirnames, filenames in os.walk(filePath):
                processLogger("I can see the files %s" % filenames)
                for filename in fnmatch.filter(filenames, '*.avi') + fnmatch.filter(filenames, '*.mkv') + fnmatch.filter(filenames, '*.iso') + fnmatch.filter(filenames, '*.mp4'):
                    if 'sample' in filename.lower():
                        continue
                    curImage = os.path.join(root, filename)
                    allMovieFileLocations.append(curImage)
                    processLogger("Found movie: " + curImage)
            if not allMovieFileLocations:
                processLogger("No files found!")
                (False, processLog[0])
        else:
            allMovieFileLocations = [filePath]

        processLogger("Renaming and Moving Movie")
        success = True
        allMovieFileLocations.sort()
        for index, curFile in enumerate(allMovieFileLocations):
            processLogger("Processing movie: " + curFile)
            try:
                extension = os.path.splitext(curFile)[1]
                if len(allMovieFileLocations) > 1:
                    newFileName = element.name + " CD" + str(index + 1) + extension
                else:
                    newFileName = element.getName() + extension
                newFileName = fixName(newFileName, self.c.replace_space_with)
                processLogger("New Filename shall be: %s" % newFileName)
                destFolder = os.path.join(destPath, fixName(element.getName(), self.c.replace_space_with))
                if not os.path.isdir(destFolder):
                    os.mkdir(destFolder)
                dest = os.path.join(destFolder, newFileName)
                processLogger("Moving File from: %s to: %s" % (curFile, dest))
                shutil.move(curFile, dest)
            except Exception, msg:
                processLogger("Unable to rename and move Movie: " + curFile + ". Please process manually")
                processLogger("given ERROR: %s" % msg)
                success = False

        processLogger("File processing done")
        # write process log
        logFileName = fixName(element.getName() + ".log", self.c.replace_space_with)
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
