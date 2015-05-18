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

import urllib
import urlparse
import time
from xdm.plugins import *
from xdm import common
import oauth2 as oauth



class OAuth(System):
    identifier = "de.lad1337.oauth"
    version = "0.1"
    single = True
    addMediaTypeOptions = False
    config = {"enabled": True}

    class OAuth(object):

        def __init__(self, consumer_key, consumer_secret,
            request_token_url=None, authorize_url=None, token_url=None,
            base_url=None,
            add_callback=True,
            headers=None):

            if base_url and base_url.endswith("/"):
                base_url = base_url[:-1]

            if request_token_url is None:
                request_token_url = base_url + "/oauth/request_token"
            self.request_token_url = request_token_url
            if authorize_url is None:
                authorize_url = base_url + "/oauth/authorize"
            self.authorize_url = authorize_url
            if token_url is None:
                token_url = base_url + "/oauth/access_token"
            self.token_url = token_url

            self.add_callback = add_callback

            self.caller_plugin = None
            self.consumer = oauth.Consumer(
                key=consumer_key, secret=consumer_secret)
            self.client = oauth.Client(self.consumer)
            self.headers = headers

        def set_plugin(self, plugin):
            self.caller_plugin = plugin

        @property
        def request_access_url(self):
            resp, content = self.client.request(
                self.request_token_url,
                "GET",
                headers=self.headers or None)
            if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])
            request_token = dict(urlparse.parse_qsl(content))
            return "{}?oauth_token={}{}".format(
                self.authorize_url,
                request_token['oauth_token'],
                "&oauth_callback=%s" % self.redirect_url if self.add_callback else ""
            )


        @property
        def redirect_url(self):
            host = common.SYSTEM.c.socket_host
            if host == "0.0.0.0":
                host = "localhost"
            protocol = "https" if common.SYSTEM.c.https else "http"
            port = common.SYSTEM.c.port
            port_suffix = "" if port == 80 else ":%s" % port
            webroot = common.SYSTEM.c.webRoot

            local_base = "{protocol}://{host}{port_suffix}{webroot}".format(
                **locals()
            )

            return "{}/oauth_token".format(local_base)
