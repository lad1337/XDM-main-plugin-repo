from xdm.plugins import *
from xdm.tasks import updateElement
from json import loads
import os

location = os.path.abspath(os.path.dirname(__file__))

class Episode(object):
    number = 0
    title = ''
    special = False
    overview = ''

    _orderBy = 'number'
    _orderReverse = True

    def getSearchTerms(self):
        return ['%s %02d' % (self.parent.title, self.number)]

        """ The user should be able to choose which anime-synonym to search for
        return ['%s %02d' % (s, self.number) for s in loads(self.parent.synonyms)]
        """

    def getTemplate(self):
        fp = os.path.join(location, "episode.ji2")
        with open (fp, "r") as template:
            return template.read()

    def get_name(self):
        return "%s e%02d %s" % (self.parent.get_name(), self.number, self.title)

    def getReleaseDate(self):
        return self.airdate

    def getIdentifier(self, tag=None):
        return self.get_field('number', tag)

class Show(object):
    title = ''
    description = ''
    poster_image = ''
    runtime = ''
    classification = ''
    id = ''
    synonyms = ''
    _orderBy = 'title'

    def get_name(self):
        return self.title

    def getIdentifier(self, tag=None):
        return self.get_field('id', tag)

    def getTemplate(self):
        fp = os.path.join(location, "show.ji2")
        with open (fp, "r") as template:
            return template.read()

    def getSearchTemplate(self):
        fp = os.path.join(location, "show_search.ji2")
        with open (fp, "r") as template:
            return template.read()


class Anime(MediaTypeManager):
    version = "0.4"
    single = True
    config = {'enabled': True,
               'page_size': 15}

    config_meta = {'plugin_desc': 'Anime support'}
    order = (Show, Episode)
    download = Episode
    identifier = 'de.lad1337.anime'
    addConfig = {}
    addConfig[Downloader] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Anime'}]
    addConfig[Indexer] = [{'type':'category', 'default': None, 'prefix': 'Category for', 'sufix': 'Anime'}]
    addConfig[PostProcessor] = [{'type':'path', 'default': None, 'prefix': 'Final path for', 'sufix': 'Anime'}]

    def headInject(self):
        return """
        <link rel="stylesheet" href="%(myUrl)s/style.css">
        <script>var uranime_page_size = %(page_size)s;</script>
        <script src="%(myUrl)s/jquery.dataTables.min.js"></script>
        <script src="%(myUrl)s/script.js"></script>
        """ % {'myUrl': self.myUrl(),
               'page_size': self.c.page_size}

    def _episode_count(self, anime, statuses=False):
        if statuses:
            return Element.objects(
                type="Episode",
                parent=anime,
                status__in=statuses
            ).count()
        else:

            return Element.objects(
                type="Episode",
                parent=anime
            ).count()
