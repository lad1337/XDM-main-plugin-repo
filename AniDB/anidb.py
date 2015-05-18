import json
from xdm.plugins import *
import simpleanidb

class Ann(Provider):
    version = "0.1"
    identifier = "de.lad1337.simpleanidb"
    screenName = 'AniDB'
    _tag = 'anidb'
    single = True
    types = ['de.lad1337.anime']
    config = {'enabled': True}
    config_meta = {'plugin_desc': 'Anime info from http://anidb.net'}

    def _mt_mtm_root(self, term):
        mtm = common.PM.getMediaTypeManager('de.lad1337.anime')[0]
        return (
            MediaType.objects.get(identifier='de.lad1337.anime'),
            mtm,
            mtm.getFakeRoot(term),
        )

    def searchForElement(self, term=''):
        self.progress.reset()
        mt, mtm, rootElement = self._mt_mtm_root(term)

        search_result = simpleanidb.Anidb().search(term)
        self.progress.total = len(search_result)

        for anime in search_result:
            self.progress.addItem()
            anime.load()
            self._createAnime(rootElement, mt, anime)

        log("%s found %s anime" % (self.name, self.progress.count))

        return rootElement

    def getElement(self, id, element=None, tag=None):
        query_id = None
        if element is not None:
            query_id = element.get_field('id', self.tag)
        if id:
            query_id = id
        if query_id is None:
            return False

        log("GET ELEMENT with id: {}".format(query_id))

        mt, mtm, root_element = self._mt_mtm_root(str(query_id))
        print root_element, root_element._get_collection(), root_element._get_collection_name()
        self._createAnime(root_element, mt, simpleanidb.Anidb().anime(query_id))

        for ele in root_element.decendants:
            if int(ele.get_field('id', self.tag)) == int(query_id):
                return ele

        return False

    def _createAnime(self, root_element, media_type, anime):

        print Element, type(Element), Element._get_collection_name()

        showElement = Element()
        showElement.media_type = media_type
        showElement.parent = root_element
        showElement.type = 'Show'
        showElement.set_field('title', unicode(anime.title), self.tag)
        showElement.set_field('id', anime.id, self.tag)
        showElement.set_field('start_date', anime.start_date, self.tag)
        showElement.set_field('end_date', anime.end_date, self.tag)
        showElement.set_field('poster_image', anime.picture.url, self.tag)
        showElement.set_field(
            'description',
            anime.description or "No description available",
            self.tag
        )
        if anime.synonyms:
            showElement.set_field(
                'synonyms',
                json.dumps(
                    [{"lang": s.lang, "title": unicode(s)}
                     for s in anime.synonyms]
                ),
                self.tag
            )
        if hasattr(anime, "official_titles") and anime.official_titles:
            showElement.set_field(
                'official_titles',
                json.dumps(
                    [{"lang": s.lang, "title": unicode(s)}
                     for s in anime.official_titles]
                ),
                self.tag
            )

        showElement.save()
        for _, _episode in anime.episodes.items():
            episode = Element()
            episode.media_type = media_type
            episode.type = 'Episode'
            episode.parent = showElement
            episode.set_field('title', unicode(_episode.title), self.tag)
            episode.set_field('number', _episode.number, self.tag)
            episode.set_field('airdate', _episode.airdate, self.tag)
            episode.save()
