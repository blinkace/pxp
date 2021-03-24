from urllib.parse import urljoin
from enum import Enum

class DTSReference:

    reftype = '<N/A>'

    def __init__(self, href, src = None):
        self.href = href
        self.src = src

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
    reftype = 'linkbaseRef'
    pass

class DTSSchema(DTSReference):
    pass

class Loc(DTSReference):
    reftype = 'loc'
    pass

class RoleRef(DTSSchema):
    reftype = 'roleRef'
    pass

class ArcroleRef(DTSSchema):
    reftype = 'arcroleRef'
    pass

class SchemaRef(DTSSchema):
    reftype = 'schemaRef'
    pass

class XSDImport(DTSSchema):
    reftype = 'import'
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
        self.dtsReferences.add(LinkbaseRef(self.resolveURL(url), src = self))

    def addLoc(self, url):
        self.dtsReferences.add(Loc(self.resolveURL(url), src = self))

    def addRoleRef(self, url):
        self.dtsReferences.add(RoleRef(self.resolveURL(url), src = self))

    def addArcroleRef(self, url):
        self.dtsReferences.add(ArcroleRef(self.resolveURL(url), src = self))

