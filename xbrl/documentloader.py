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

    def getDocument(self, href):
        return self.documents[href]

    def loadDTSReference(self, ref):
        doc = self.documents.get(ref.href, None)
        if doc is not None:
            logging.debug("%s loaded from cache" % ref.href)
            return doc

        logging.debug("Fetching %s " % ref.href)

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
        self.documents[ref.href] = doc
        return doc
