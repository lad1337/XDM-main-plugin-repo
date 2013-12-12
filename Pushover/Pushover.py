# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://github.com/lad1337/XDM-main-plugin-repo/
#
# This file is part of a XDM plugin.
#
# XDM plugin.
# Copyright (C) 2013  Dennis Lutter
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from xdm.plugins import *
import requests

XDM_PUSHOVER_PROVIDER_KEY = 'ajHCoK7Uz1wt36AGs3yVZGMtWZhLL9'


class Pushover(Notifier):
    version = "0.1"
    identifier = "de.lad1337.pushover.app"
    screenName = "Pushover"
    addMediaTypeOptions = False
    _config = {'user_key': ''}

    def _sendTest(self, user_key):
        log("Testing Pushover")
        result = self._sendMessage("Test from XDM", user_key, None)
        if result:
            return (result, {}, 'Message send. Check your device(s)')
        else:
            return (result, {}, 'Message NOT send. Check your User Key')
    _sendTest.args = ['user_key']

    def _sendEnabled(self):
        self.sendMessage("You just enabled Pushover on XDM")

    def sendMessage(self, msg, element=None):
        if not self.c.user_key:
            log.error("Pushover User Key not set")
            return False
        return self._sendMessage(msg, self.c.user_key, element)

    def _sendMessage(self, msg, user_key, element):
        payload = {"token": XDM_PUSHOVER_PROVIDER_KEY,
                   "user" : user_key,
                   "message": msg,
                   }
        try:
            r = requests.post("https://api.pushover.net/1/messages.json", data=payload)
        except requests.ConnectionError:
            log.error('Sending notification failed, no internet ?')
            return False
        log("pushover url: %s payload: %s" % (r.url, payload))
        log("pushover code %s" % r.status_code)
        if not r.status_code == requests.codes.ok:
            log.error('Sending notification failed :(')
            return False

        return True

    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'enabled': {'on_enable': [_sendEnabled]},
                   'plugin_buttons': {'sendTest': {'action': _sendTest, 'name': 'Send test'}},
                   'plugin_desc': 'Simple Pushover notifier. THis uses the XDM Application. Get your user key from https://pushover.net/'
                   }
