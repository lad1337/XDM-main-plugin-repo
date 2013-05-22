from xdm.plugins import *
import jsonrpclib

class XBMC(Notifier):
    version = "0.2"
    identifier = 'de.lad1337.movies.xbmc'
    screenName = 'XBMC Notifier'
    addMediaTypeOptions = False
    _config = {'host': 'http://localhost',
                'port': 8080}


    def _createServer(self, host, port):
        if not host.startswith('http'):
            host = 'http://%s' % host
        url = '%s:%s/jsonrpc' % (host, port)
        log('XBMC JSONrpc set to %s' % url)
        return jsonrpclib.Server(url)
        

    def _sendTest(self, host, port):
        server = self._createServer(host, port)
        try:
            result = server.GUI.ShowNotification(title='XDM', message='Test from XDM')
        except Exception as ex:
            return (False, {}, 'An error while sending the test: %s' % ex)
        return (result == 'OK', {}, '')
    _sendTest.args = ['host', 'port']

    def sendMessage(self, msg, element=None):
        if element is None:
            return True
        server = self._createServer(self.c.host, self.c.port)

        if element.status in common.getCompletedStatuses():
            server.VideoLibrary.Scan()

        server.GUI.ShowNotification(title='XDM', message=msg)


    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'plugin_buttons': {'sendTest': {'action': _sendTest, 'name': 'Send test'}},
                   'plugin_desc': 'XBMC notifier. Sends screen messages and issues a library scan on a "complet" status.'
                   }
