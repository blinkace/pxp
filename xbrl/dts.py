from .const import NS
from .xml.taxonomy.schemadocument import SchemaDocument
from lxml import etree
from .model.taxonomy import Concept, Taxonomy, TypedDimension, Datatype
from .xbrlerror import XBRLError
from xbrl.xml import qname
from urllib.parse import urldefrag, urlparse

class DTS:

    def __init__(self, documentCache):
        self.documents = set()
        self.documentCache = documentCache

    def addDocument(self, url):
        self.documents.add(url)

    def getDocument(self, url):
        if url not in self.documents:
            print(url)
            raise XBRLError("outOfDTSReference", "Reference to '%s' is not in the DTS" % (url))
        return self.documentCache.getDocument(url)

    def getElementByURL(self, url):
        doc = self.getDocument(urldefrag(url).url)
        u = urlparse(url)
        return doc.getElementById(u.fragment)



        


    def buildTaxonomy(self):
        taxonomy = Taxonomy()
        for url in self.documents:
            d = self.documentCache.getDocument(url)
            if isinstance(d, SchemaDocument):
                if d.preferredPrefix is not None:
                    taxonomy.addPrefix(d.preferredPrefix, d.targetNamespace)
                for n, e in d.elements.items():
                    if qname('xbrli:item') in e.substitutionGroups():

                        datatype = Datatype(e.datatypeChain())
                        if datatype.itemType is None:
                            raise XBRLError("xbrl21e:invalidItemType", "Concept '%s' is not derived from an XBRL Item Type" % e.name, spec_ref = '5.1.1.3')

                        conceptName = etree.QName(d.targetNamespace, e.name)
                        if e.typedDomainRef:
                            tde = self.getElementByURL(d.resolveURL(e.typedDomainRef))
                            print(tde.name)
                            print(list(dt.text for dt in tde.datatypeChain()))
                            c = TypedDimension(
                                conceptName,
                                datatype,
                                e.substitutionGroups(),
                                Datatype(tde.datatypeChain())
                                )
                        else:
                            c = Concept(
                                    conceptName,
                                    datatype,
                                    e.substitutionGroups()
                                    )

                        taxonomy.addConcept(c)

        return taxonomy










