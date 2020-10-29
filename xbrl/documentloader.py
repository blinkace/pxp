from .xml.taxonomy.schemaparser import SchemaParser
from .xml.taxonomy.linkbaseparser import LinkbaseParser
from .xml.taxonomy.document import DTSSchema, LinkbaseRef, Loc
from .dts import DTS
from lxml import etree
from .xbrlerror import XBRLError
import xbrl.xml
from xbrl.xml import qname
import logging

class DocumentLoader:

    def __init__(self, url_resolver):
        self.queue = []
        self.documents = dict()
        self.url_resolver = url_resolver

    def load(self, entry):
        dts = DTS(documentCache = self)
        for r in entry:
            self.enqueue(r)
        self.discover(dts)
        return dts

    def discover(self, dts):
        while len(self.queue) > 0:
            ref = self.queue[0]
            self.queue = self.queue[1:]
            doc = self.loadDTSReference(ref)
            logging.info("Loaded %s" % ref.href)
            dts.addDocument(ref.href)
            self.documents[ref.href] = doc
            for d in doc.dtsReferences:
                self.enqueue(d)


    def loadDTSReference(self, ref):

        with self.url_resolver.open(ref.href) as src:
            tree = etree.parse(src, xbrl.xml.parser())
        root = tree.getroot()

        isSchema = root.tag == qname("xs:schema")
        isLinkbase = root.tag == qname("link:linkbase")

        if isinstance(ref, DTSSchema) and not isSchema:
            raise XBRLError("xbrl21e:invalidDTSReferenceTarget", "Expected schema but found %s when loading %s" % (root.tag, ref.href))

        if isinstance(ref, LinkbaseRef) and not isLinkbase:
            raise XBRLError("xbrl21e:invalidLinbaseRefTarget", "Expected linkbase but found %s when loading %s" % (root.tag, ref.href), spec_ref = "4.3.2")

        if isSchema:
            parser = SchemaParser()
        elif isLinkbase:
            parser = LinkbaseParser()
        else:
            raise ValueError("Unknown document type with root element %s" % root.tag)
        doc = parser.parse(tree, ref.href)
        doc.documentCache = self
        return doc

    def loadSchema(self, url):
        return parser.parse(url)

    def loadLinkbase(self, url):
        parser = LinkbaseParser(url_resolver = self.url_resolver)
        return parser.parse(url)

    def enqueue(self, ref):
        if ref.href not in self.documents:
            self.documents[ref.href] = None
            self.queue.append(ref)


    def getDocument(self, href):
        return self.documents[href]
