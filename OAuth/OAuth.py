# Author: Dennis Lutter <lad1337@gmail.com>
# URL: https://github.com/lad1337/XDM-main-plugin-repo/
#
# This file is part of a XDM plugin.
#
# XDM plugin.
# Copyright (C) 2015  Dennis Lutter
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

import json
from xdm.plugins import *
from xdm import common

from requests_oauthlib import OAuth1Session
from oauthlib.oauth1 import Client

from requests_oauthlib import OAuth2Session


def redirect_url_base():
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

    return "{}/oauth".format(local_base)

def save_tokens(plugin, tokens):
    for key, value in tokens.items():
        setattr(plugin.hc, key, value)


class MyHeaderClientOAuth1(Client):
    def __init__(self, *args, **kwargs):
        self.extra_headers = kwargs.pop("extra_headers") if "extra_headers" in kwargs else None
        super(MyHeaderClientOAuth1, self).__init__(*args, **kwargs)

    def _render(self, *args, **kwargs):
        uri, headers, body = super(MyHeaderClientOAuth1, self)._render(*args, **kwargs)
        if self.extra_headers:
            headers.update(self.extra_headers)
        return uri, headers, body

class OAuthBase(object):

    def _init_session(self):
        pass

    def set_plugin(self, plugin):
        self.plugin = plugin
        self._init_session()
        if not self.authorized:
            self.message_user_to_authenticate()

    def info(self):
        data = self._info()
        return True, data, "OAuth info"

    @property
    def authorized(self):
        return self.session.authorized

    def reset(self):
        for key in self.keys:
            setattr(self.plugin.hc, key, "")
        self._init_session()

    def message_user_to_authenticate(self):
        common.MM.createWarning(
            "{plugin} authentication".format(plugin=self.plugin),
            confirmJavascript="oauth_start(this, '{p.identifier}', '{p.instance}')".format(
                p=self.plugin
            ),
            uuid="oauth_warning_{p.identifier}_{p.instance}".format(
                p=self.plugin
            )
        )

class OAuth(System):
    identifier = "de.lad1337.oauth"
    version = "0.1"
    single = True
    addMediaTypeOptions = False
    config = {"enabled": True}

    class OAuth2(OAuthBase):
        keys = [
            "oauth_token_keys", "token_type", "refresh_token", "access_token",
            "scope", "created_at", "expires_in", "expires_at"]

        def __init__(self,
            client_id,
            client_secret,
            scope=None,
            headers=None,
            authorization_url=None,
            token_url=None):

            self.authorization_url = authorization_url
            self.token_url = token_url

            self.plugin = None
            self.session = None
            self.client_id = client_id
            self.client_secret = client_secret
            self.scope = scope
            self.headers = headers or {}

        def _init_session(self, verifier=None):
            self.session = OAuth2Session(
                self.client_id,
                scope=self.scope,
                redirect_uri=self.callback_uri,
                token=self.token
            )
            log.debug("OAuth2: init session for: {} Authorized: {}".format(
                self.plugin, self.authorized))

        def _info(self):
            return self.token

        @property
        def callback_uri(self):
            return "{base}/v2/".format(base=redirect_url_base())

        @property
        def request_access_url(self):
            self.reset()
            state = "{p.identifier}|{p.instance}".format(p=self.plugin)
            url, _ = self.session.authorization_url(
                self.authorization_url,
                state=state
            )
            return url

        def get_access_token(self, code):
            oauth_tokens = self.session.fetch_token(
                self.token_url,
                code=code,
                client_secret=self.client_secret
            )
            for key, value in oauth_tokens.items():
                if key == "scope":
                    value = json.dumps(value)
                setattr(self.plugin.hc, key, value)
            self.plugin.hc.oauth_token_keys = json.dumps(oauth_tokens.keys())
            return self.authorized

        @property
        def token(self):
            try:
                oauth_token_keys = json.loads(self.plugin.hc.oauth_token_keys)
            except (ValueError, AttributeError):
                return
            token = {}
            for key in oauth_token_keys:
                value = getattr(self.plugin.hc, key)
                if key == "scope":
                    value = json.loads(value)
                token[key] = value
            return token

        @property
        def access_token(self):
            return self.token["access_token"]


    class OAuth1(OAuthBase):
        keys = [
            "resource_owner_key",
            "resource_owner_secret",
            "oauth_token",
            "oauth_token_secret"]

        def __init__(self,
            consumer_key,
            consumer_secret,
            request_token_url=None,
            authorize_url=None,
            token_url=None,
            headers=None
            ):

            self.request_token_url = request_token_url
            self.authorize_url = authorize_url
            self.token_url = token_url

            self.plugin = None
            self.session = None
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
            self.headers = headers or {}

        def _init_session(self, verifier=None):
            self.session = OAuth1Session(
                self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.resource_owner_key,
                resource_owner_secret=self.resource_owner_secret,
                callback_uri=self.callback_uri,
                client_class=MyHeaderClientOAuth1,
                extra_headers=self.headers,
                verifier=verifier
            )
            log.debug("OAuth1: init session for: {} Authorized: {}".format(
                self.plugin, self.authorized))


        def _info(self):
            return dict(
                consumer_key=self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.resource_owner_key,
                resource_owner_secret=self.resource_owner_secret,
                extra_headers=self.headers
            )

        @property
        def callback_uri(self):
            return "{base}/v1/{p.identifier}|{p.instance}".format(
                base=redirect_url_base(),
                p=self.plugin
            )

        @property
        def resource_owner_key(self):
            try:
                return self.plugin.hc.resource_owner_key or None
            except AttributeError:
                return None

        @property
        def resource_owner_secret(self):
            try:
                return self.plugin.hc.resource_owner_secret or None
            except AttributeError:
                return None

        @property
        def request_access_url(self):
            self.reset()
            fetch_response = self.session.fetch_request_token(self.request_token_url)
            # we need to transform these keys, so they get added to the
            # session in the next step
            save_tokens(self.plugin, {
                "resource_owner_key": fetch_response["oauth_token"],
                "resource_owner_secret": fetch_response["oauth_token_secret"]
                })
            return self.session.authorization_url(self.authorize_url)

        def get_access_token(self, oauth_token, oauth_verifier):
            self._init_session(oauth_verifier)
            """
            self.session.parse_authorization_response(
                "foo?oauth_token={oauth_token}&oauth_verifier={oauth_verifier}".format(
                    oauth_token=oauth_token,
                    oauth_verifier=oauth_verifier
                )
            )
            """
            oauth_tokens = self.session.fetch_access_token(self.token_url)
            save_tokens(self.plugin, oauth_tokens)
            return self.authorized
