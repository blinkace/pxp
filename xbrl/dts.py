from .const import NS
from .schemadocument import SchemaDocument
from lxml import etree
from .model.taxonomy import Concept, Taxonomy
from .xbrlerror import XBRLError

class DTS:

    def __init__(self):
        self.documents = dict()

    def addDocument(self, url, doc):
        doc.setDTS(self)
        self.documents[url] = doc

    def getDocument(self, url):
        return self.documents[url]

    def buildTaxonomy(self):

        taxonomy = Taxonomy()
        for url, d in self.documents.items():
            if isinstance(d, SchemaDocument):
                for n, e in d.elements.items():
                    if etree.QName(NS['xbrli'], 'item') in e.substitutionGroups():
                        itemType = next((dt for dt in e.datatypeChain() if dt.namespace == NS['xbrli']), None)
                        if itemType is None:
                            raise XBRLError("xbrl21e:invalidItemType", "Concept '%s' is not derived from an XBRL Item Type" % e.name, spec_ref = '5.1.1.3')
                        c = Concept(etree.QName(d.targetNamespace, e.name), itemType)
                        taxonomy.addConcept(c)

        return taxonomy







