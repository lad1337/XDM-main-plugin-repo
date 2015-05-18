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
import shutil
from os import path


class Mover(PostProcessor):
    version = "0.2"
    identifier = 'de.lad1337.simple.mover'
    screenName = 'Mover'
    types = []
    config = {'copy': False}
    config_meta = {'plugin_desc': 'This will move the final download folder to the given destination.',
                   'copy': {'desc': 'If this is on the Folder will be copied instead of moved.'}}
    useConfigsForElementsAs = 'Path'

    def __init__(self, instance='Default'):
        for mtm in common.PM.getMediaTypeManager():
            prefix = self.useConfigsForElementsAs
            sufix = mtm.type
            h_name = '%s for %s' % (prefix, sufix)
            c_name = helper.replace_some('%s %s %s' % (mtm.name, prefix.lower(), sufix))
            self.config[c_name] = None
            self.config_meta[c_name] = {
                'human': h_name,
                'type': self.useConfigsForElementsAs.lower(),
                'mediaType': mtm.mt,
                'element': mtm.root}

        PostProcessor.__init__(self, instance=instance)


    def postProcessPath(self, element, srcPath):
        destPath = self._getPath(element)
        log("Destination for %s is %s" %(srcPath, destPath))
        if self.c.copy:
            msg = "Copying %s to %s" % (srcPath, destPath)
            shutil.copytree(srcPath, destPath)
        else:
            msg = "Moving %s to %s" % (srcPath, destPath)
            shutil.move(srcPath, destPath)

        log.info(msg)
        final_location = path.abspath(path.join(destPath, path.basename(srcPath)))
        return (True, final_location, msg)

