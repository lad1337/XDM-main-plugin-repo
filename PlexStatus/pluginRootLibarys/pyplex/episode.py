from video import Video
from media import Media
class Episode(Video):

    def __init__(self, element, server):
        super(Episode, self).__init__(element, server)

        self.type = 'episode'
        for key in element.keys():
            setattr(self, key, element.attrib[key])
        try:
            self.index = int(element.attrib['index'])
        except KeyError as e:
            #print "Missing key in element: ", e.message
            pass

    def __str__(self):
        return "<Episode: {self.title} {self.parentIndex}:{self.index}>".format(self=self)

    def __repr__(self):
        return self.__str__()

