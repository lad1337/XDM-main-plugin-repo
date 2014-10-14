
from xml.etree.ElementTree import XML
import requests

from library import Library
from client import Client

class Server(object):

    def __init__(self, address, port=32400):
        # TODO: clean up address, remove http:// etc

        # remove slash at end of address
        if address[-1] == '/':
            address = address[:-1]
        self.address = address
        self.port = int(port)

    @property
    def url(self):
        return "http://%s:%d" % (self.address, self.port)



    def execute(self, path):
        if path[0] == '/':
            path = path[1:]

        return requests.get(
            "{}/{}".format(self.url, path)
        ).text



    def query(self, path):
        element = XML(
            self.execute(path).encode("utf-8")
        )
        return element


    def __str__(self):
        return "<Server: %s/>" % self.url

    def __repr__(self):
        return "<Server: %s/>" % self.url


    @property
    def library(self):
        elem = self.query("/library")
        return Library(self)

    @property
    def clients(self):
        elem = self.query("/clients")
        clist = [Client(e, self) for e in elem]
        return clist

