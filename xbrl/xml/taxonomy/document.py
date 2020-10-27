from urllib.parse import urljoin
from enum import Enum

class DTSReference:

    def __init__(self, href):
        self.href = href

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.href == other.href
        )

    def __repr__(self):
        return "%s[%s]" % (type(self).__name__, self.href)

    def __hash__(self):
        return hash(self.href)

class LinkbaseRef(DTSReference):
    pass

class DTSSchema(DTSReference):
    pass

class Loc(DTSReference):
    pass

class RoleRef(DTSSchema):
    pass

class ArcroleRef(DTSSchema):
    pass

class SchemaRef(DTSSchema):
    pass

class XSDImport(DTSSchema):
    pass

class DTSDocument:

    def __init__(self, url):
        self.url = url
        self.dtsReferences = set()

    def setDTS(self, dts):
        self.dts = dts

    def resolveURL(self, url):
        return urljoin(self.url, url)

    def addLinkbaseRef(self, url):
        self.dtsReferences.add(LinkbaseRef(self.resolveURL(url)))

    def addLoc(self, url):
        self.dtsReferences.add(Loc(self.resolveURL(url)))

    def addRoleRef(self, url):
        self.dtsReferences.add(RoleRef(self.resolveURL(url)))

    def addArcroleRef(self, url):
        self.dtsReferences.add(ArcroleRef(self.resolveURL(url)))

