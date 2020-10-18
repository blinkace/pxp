from .const import NS
from .schemadocument import SchemaDocument
from lxml import etree
from .model.taxonomy import Concept, Taxonomy
from .xbrlerror import XBRLError

class DTS:

    def __init__(self, documentCache):
        self.documents = set()
        self.documentCache = documentCache

    def addDocument(self, url):
        self.documents.add(url)

    def getDocument(self, url):
        return self.documents[url]

    def buildTaxonomy(self):
        taxonomy = Taxonomy()
        for url in self.documents:
            d = self.documentCache.getDocument(url)
            if isinstance(d, SchemaDocument):
                if d.preferredPrefix is not None:
                    taxonomy.addPrefix(d.preferredPrefix, d.targetNamespace)
                for n, e in d.elements.items():
                    if etree.QName(NS['xbrli'], 'item') in e.substitutionGroups():
                        itemType = next((dt for dt in e.datatypeChain() if dt.namespace == NS['xbrli']), None)
                        if itemType is None:
                            raise XBRLError("xbrl21e:invalidItemType", "Concept '%s' is not derived from an XBRL Item Type" % e.name, spec_ref = '5.1.1.3')
                        c = Concept(
                                etree.QName(d.targetNamespace, e.name), 
                                itemType, 
                                isDimension = (etree.QName(NS['xbrldt'], "dimensionItem") in e.substitutionGroups())
                                )
                        taxonomy.addConcept(c)

        return taxonomy







