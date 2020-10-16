from .schemaparser import SchemaParser
from .linkbaseparser import LinkbaseParser
from .document import DTSSchema, LinkbaseRef, Loc
from .dts import DTS
from lxml import etree
from .const import NS
from .xbrlerror import XBRLError
import logging

class DocumentLoader:

    def __init__(self, url_resolver):
        self.queue = []
        self.documents = set()
        self.dts = None
        self.url_resolver = url_resolver

    def load(self, entry):
        self.dts = DTS()
        for r in entry:
            self.enqueue(r)
        self.discover()
        return self.dts

    def discover(self):
        while len(self.queue) > 0:
            ref = self.queue[0]
            self.queue = self.queue[1:]
            doc = self.loadDTSReference(ref)

            if doc is not None:
                logging.info("Loaded %s" % ref.href)
                self.dts.addDocument(ref.href, doc)
                for d in doc.dtsReferences:
                    self.enqueue(d)


    def loadDTSReference(self, ref):

        with self.url_resolver.open(ref.href) as src:
            tree = etree.parse(src)
        root = tree.getroot()

        isSchema = root.tag == etree.QName(NS["xsd"], "schema")
        isLinkbase = root.tag == etree.QName(NS["link"], "linkbase")

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
        return parser.parse(tree, ref.href)

    def loadSchema(self, url):
        return parser.parse(url)

    def loadLinkbase(self, url):
        parser = LinkbaseParser(url_resolver = self.url_resolver)
        return parser.parse(url)

    def enqueue(self, ref):
        if ref.href not in self.documents:
            self.documents.add(ref.href)
            self.queue.append(ref)

