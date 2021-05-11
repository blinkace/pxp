import json
from xbrl.xml import parser, qname
import lxml.etree as etree
from urllib.parse import urlparse
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UnknownDocumentClassError(Exception):
    pass

class MissingDocumentClassError(Exception):
    pass

class DocumentClass(Enum):
    XBRL_2_1 = 1
    INLINE_XBRL = 2
    XBRL_JSON = 3
    XBRL_CSV = 4
    REPORT_PACKAGE = 5

    def identify(resolver, url):
        purl = urlparse(url)
        if purl.scheme != 'zip' and purl.path.lower().endswith(".zip"):
            return DocumentClass.REPORT_PACKAGE
        with resolver.open(url) as fin:
            try:
                j = json.load(fin)
                dt = j.get("documentInfo",{}).get("documentType", None)
                if dt is not None:
                    if dt.endswith("xbrl-csv"):
                        return DocumentClass.XBRL_CSV
                    if dt.endswith("xbrl-json"):
                        return DocumentClass.XBRL_JSON
                    raise UnknownDocumentClassError("Unknown document type: %s" % dt)

                raise MissingDocumentClassError("Input file is valid JSON, but does not contain a document type")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        with resolver.open(url) as fin:
            try:
                root = etree.parse(fin, parser()).getroot()
                if root.tag == qname("xbrli:xbrl"):
                    return DocumentClass.XBRL_2_1
                if root.tag == qname("xhtml:html"):
                    return DocumentClass.INLINE_XBRL
                logger.debug("Found XML root element: %s" % root.tag)
            except etree.LxmlError as e:
                logger.debug("Document is invalid XML: %s" % str(e))
                pass
        return None









