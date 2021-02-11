from .const import NS
from .xml.taxonomy.schemadocument import SchemaDocument
from lxml import etree
from .model.taxonomy import Concept, Taxonomy, TypedDimension, Datatype, PeriodType
from .xbrlerror import XBRLError
from xbrl.xml import qname
from urllib.parse import urldefrag, urlparse
import logging

class DTS:

    def __init__(self, entryPoint, documentCache):
        self.documents = dict()
        self.entryPoint = entryPoint
        self.documentCache = documentCache

    def discover(self):
        self.queue = []
        for ep in self.entryPoint:
            self.enqueue(ep)

        while len(self.queue) > 0:
            ref = self.queue[0]
            self.queue = self.queue[1:]

            # Already loaded this document, so just remove it from the queue
            # and continue
            if ref.href in self.documents:
                continue

            doc = self.documentCache.loadDTSReference(ref)
            logging.info("Loaded %s" % ref.href)
            self.documents[ref.href] = doc
            for d in doc.dtsReferences:
                self.enqueue(d)

    def loadSchema(self, url):
        return parser.parse(url)

    def loadLinkbase(self, url):
        parser = LinkbaseParser(url_resolver = self.url_resolver)
        return parser.parse(url)

    def enqueue(self, ref):
        if ref.href not in self.documents:
            self.queue.append(ref)

    def addDocument(self, url):
        self.documents.add(url)

    def getDocument(self, url):
        if url not in self.documents:
            raise XBRLError("outOfDTSReference", "Reference to '%s' is not in the DTS" % (url))
        return self.documentCache.getDocument(url)

    def getElementByURL(self, url):
        doc = self.getDocument(urldefrag(url).url)
        u = urlparse(url)
        return doc.getElementById(u.fragment)

    def buildTaxonomy(self):
        taxonomy = Taxonomy(self.entryPoint)
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
                        if e.periodType is None:
                            raise XBRLError("xbrl21e:missingPeriodType", "Concept '%s' does not have a period type" % e.name)
                        periodType = PeriodType.INSTANT if e.periodType == 'instant' else PeriodType.DURATION
                        if e.typedDomainRef:
                            tde = self.getElementByURL(d.resolveURL(e.typedDomainRef))
                            if not tde.isComplex:
                                tddt = Datatype(tde.datatypeChain()) 
                            else:
                                tddt = None
                            c = TypedDimension(
                                conceptName,
                                datatype,
                                e.substitutionGroups(),
                                tddt,
                                periodType
                                )
                        else:
                            c = Concept(
                                    conceptName,
                                    datatype,
                                    e.substitutionGroups(),
                                    periodType,
                                    e.isAbstract
                                    )

                        taxonomy.addConcept(c)

        return taxonomy










