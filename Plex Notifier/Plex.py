from xdm.plugins import *
from xdm import helper
import requests
import xml.etree.ElementTree as ET

class Plex(Notifier):
    version = "0.3"
    identifier = 'de.lad1337.movies.plex'
    screenName = 'Plex Notifier'
    addMediaTypeOptions = "runFor"
    _config = {'host': 'http://localhost',
               'port': 32400,
               'section_select': ''}


    def _createUrl(self, host, port):
        if not host.startswith('http'):
            host = "http://%s" % host

        return "%s:%s" % (host, port)

    def _getSections(self, host, port):
        basic_url = self._createUrl(host, port)
        r = requests.get("%s/library/sections" % basic_url)
        root = ET.fromstring(r.content)
        sections = {}
        for directory in root.findall('Directory'):
            sections[directory.get('key')] = directory.get('title')

        return sections

    def _get_sections_ajax(self, host, port):
        sections = self._getSections(host, port)

        dataWrapper = {'callFunction': 'plex_' + self.instance + '_fillSections',
                       'functionData': sections}

        return (True, dataWrapper, 'I found %s sections please select one.' % len(sections))
    _get_sections_ajax.args = ['host', 'port']

    def _sendTest(self, host, port):
        basic_url = self._createUrl(host, port)
        try:
            r = requests.get("%s/" % basic_url)
        except Exception as ex:
            log.error("Error during _sendTest to Plex")
            # TODO: dont use puny replace
            # see http://stackoverflow.com/questions/701704/convert-html-entities-to-unicode-and-vice-versa
            return (False, {}, 'Error while sending the test: %s' % str(ex).replace('<', '').replace('>', ''))
        if r.status_code == requests.codes.ok:
            return (True, {}, 'OK')
        else:
            return (False, {}, 'Failed. No idea why but we got a status code: %d' % r.status_code)

    _sendTest.args = ['host', 'port']

    def _section_select(self):
        if not self.c.host or not self._sendTest(self.c.host, self.c.port)[0]:
            return {}
        return self._getSections(self.c.host, self.c.port)

    def sendMessage(self, msg, element=None):
        if element is None:
            return True
        basic_url = self._createUrl(self.c.host, self.c.port)

        if element.status in common.getCompletedStatuses():
            requests.get("%s/library/sections/%s/refresh" % (basic_url, self.c.section_select))

    def getConfigHtml(self):
        return """<script>
                function plex_""" + self.instance + """_fillSections(data){
                  var select = $('#""" + helper.idSafe(self.name) + """ select[name$="section_select"]');
                  console.log(data, select);
                  $.each(data, function(key,title){
                      select.append('<option value="'+key+'">'+title+'</option>')
                  });
                };
                </script>
        """


    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'plugin_buttons': {'sendTest': {'action': _sendTest, 'name': 'Send test'},
                                      'getSections': {'action': _get_sections_ajax, 'name': 'Get sections'}},
                   'plugin_desc': 'Plex notifier. Issues a library scan on "complete" status.'
                   }
