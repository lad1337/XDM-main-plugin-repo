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
    _config = {'enabled': True}
    config_meta = {'plugin_desc': 'Anime info from http://anidb.net'}

    def _mt_mtm_root(self, term):
        mtm = common.PM.getMediaTypeManager('de.lad1337.anime')[0]
        return (
            MediaType.get(MediaType.identifier == 'de.lad1337.anime'),
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
            query_id = element.getField('id', self.tag)
        if id:
            query_id = id
        if query_id is None:
            return False

        log("GET ELEMENT with id: {}".format(query_id))

        mt, mtm, root_element = self._mt_mtm_root(str(query_id))
        self._createAnime(root_element, mt, simpleanidb.Anidb().anime(query_id))

        for ele in root_element.decendants:
            if int(ele.getField('id', self.tag)) == int(query_id):
                return ele

        return False

    def _createAnime(self, rootElement, mediaType, anime):

        showElement = Element()
        showElement.mediaType = mediaType
        showElement.parent = rootElement
        showElement.type = 'Show'
        showElement.setField('title', unicode(anime.title), self.tag)
        showElement.setField('id', anime.id, self.tag)
        showElement.setField('start_date', anime.start_date, self.tag)
        showElement.setField('end_date', anime.end_date, self.tag)
        if anime.picture:
            showElement.setField('poster_image', anime.picture.url, self.tag)
        showElement.setField(
            'description',
            anime.description or "No description available",
            self.tag
        )

        if anime.synonyms:
            showElement.setField(
                'synonyms',
                json.dumps(
                    [{"lang": s.lang, "title": unicode(s)}
                     for s in anime.synonyms]
                ),
                self.tag
            )


        if hasattr(anime, "official_titles") and anime.official_titles:
            showElement.setField(
                'official_titles',
                json.dumps(
                    [{"lang": s.lang, "title": unicode(s)}
                     for s in anime.official_titles]
                ),
                self.tag
            )

        showElement.saveTemp()
        for _, _episode in anime.episodes.items():
            episode = Element()
            episode.mediaType = mediaType
            episode.type = 'Episode'
            episode.parent = showElement
            episode.setField('title', unicode(_episode.title), self.tag)
            episode.setField('number', _episode.number, self.tag)
            episode.setField('airdate', _episode.airdate, self.tag)
            episode.saveTemp()
