from xdm.plugins import *
import jsonrpclib

class XBMC(Notifier):
    version = "0.4"
    identifier = 'de.lad1337.movies.xbmc'
    screenName = 'XBMC Notifier'
    addMediaTypeOptions = False
    _config = {'host': 'http://localhost',
               'port': 8080,
               'username': '',
               'password': ''}


    def _createServer(self, host, port, username, password):
        if host.startswith('http://'):
            host = host.replace('http://', '')
        if username:
            url = '%s:%s@%s:%s/jsonrpc' % (username, password, host, port)
        else:
            url = '%s:%s/jsonrpc' % (host, port)
        if not url.startswith('http'):
            url = 'http://%s' % url
        log('XBMC JSONrpc set to %s' % url, {username:'##username##', password:'##password##'})
        return jsonrpclib.Server(url)


    def _sendTest(self, host, port, username, password):
        server = self._createServer(host, port, username, password)
        try:
            result = server.GUI.ShowNotification(title='XDM', message='Test from XDM')
        except Exception as ex:
            log.error("Error during _sendTest to XBMC", {username:'##username##', password:'##password##'})
            # TODO: dont use puny replace
            # see http://stackoverflow.com/questions/701704/convert-html-entities-to-unicode-and-vice-versa
            return (False, {}, 'Error while sending the test: %s' % str(ex).replace('<', '').replace('>', ''))
        if result == 'OK':
            return (True, {}, 'OK')
        else:
            return (False, {}, 'Failed')

    _sendTest.args = ['host', 'port', 'username', 'password']

    def sendMessage(self, msg, element=None):
        if element is None:
            return True
        server = self._createServer(self.c.host, self.c.port, self.c.username, self.c.password)

        if element.status in common.getCompletedStatuses():
            server.VideoLibrary.Scan()

        server.GUI.ShowNotification(title='XDM', message=msg)


    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'plugin_buttons': {'sendTest': {'action': _sendTest, 'name': 'Send test'}},
                   'plugin_desc': 'XBMC notifier. Sends screen messages (always) and issues a library scan (only on "complete" status).'
                   }
