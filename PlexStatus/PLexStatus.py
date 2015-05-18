
from xdm.plugins import *

from pyplex.server import Server as PlexServer

CHANGE_ON = [common.IGNORE, common.PP_FAIL]
CHANGE_TO = common.DOWNLOADED

class PlexStatus(MediaAdder):
    version = "0.4"
    identifier = "de.lad1337.plexstatus"
    addMediaTypeOptions = False
    config = {'host': 'localhost',
               'port': 32400}

    config_meta = {'plugin_desc': 'Sets the status of Episodes to {} if found in plex. But only for {} episodes'.format(
        CHANGE_TO,
        ",".join(map(str, CHANGE_ON))
    )}
    types = ['de.lad1337.tv']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def _get_all_names(self, show, xem_name_plugin):
        if xem_name_plugin is None:
            return [show.title]
        else:
            xem_names = [show.title]
            for xem_name_data in xem_name_plugin._names_for_show(show):
                for xem_name, season in xem_name_data.items():
                    xem_names.append(xem_name)
            return xem_names

    def runShedule(self):
        if not self.c.host:
            return []
        server = PlexServer(self.c.host, self.c.port)

        mtm = common.PM.getMediaTypeManager("de.lad1337.tv")[0]

        xem_name_plugin = None
        try:
            xem_name_plugin = common.PM.getSearchTermFilters("de.lad1337.xem.names")[0]
        except IndexError:
            log("plugin de.lad1337.xem.names not installed no alternative title search on plex")
        else:
            if tuple(map(int, xem_name_plugin.version.split("."))) < (0, 3):
                log("plugin de.lad1337.xem.names lower version then 0.3")
                xem_name_plugin = None

        shows = Element.select().where(Element.type == 'Show',
                                       Element.parent == mtm.root)
        for show in shows:
            show_titles = self._get_all_names(show, xem_name_plugin)
            for title in show_titles:
                try:
                    plex_show = server.library.findShows(title)[0]
                except IndexError:
                    log.warning("could not find {} in plex".format(title))
                    continue
                else:
                    break
            else:
                continue

            seasons = list(show.children)
            plex_seasons = plex_show.seasons

            for season in seasons:

                plex_season = [s for s in plex_seasons if s.index == season.number]
                if not plex_season:
                    log.debug("seasons {season.number} not found in plex".format(season=season))
                    continue
                plex_season = plex_season[0]

                episodes = list(season.children)
                plex_episodes = plex_season.episodes
                for episode in episodes:
                    if episode.status not in CHANGE_ON:
                        continue
                    plex_episode  = [
                        e for e in plex_episodes if e.index == episode.number]
                    if not plex_episode:
                        log.debug(
                            u"episode {episode} not found in plex".format(
                                episode=episode))
                        continue

                    episode.status = CHANGE_TO
                    log.info(
                        u"plex status setting {} to {}".format(
                            episode, episode.status))
                    episode.save()

        return []
