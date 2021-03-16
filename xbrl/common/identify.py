import json
from xbrl.xml import parser, qname
import lxml.etree as etree
from enum import Enum

class UnknownDocumentClassError(Exception):
    pass

class MissingDocumentClassError(Exception):
    pass

class DocumentClass(Enum):
    XBRL_2_1 = 1
    INLINE_XBRL = 2
    XBRL_JSON = 3
    XBRL_CSV = 4

    def identify(resolver, url):
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
            except json.JSONDecodeError:
                pass
        with resolver.open(url) as fin:
            try:
                root = etree.parse(fin, parser()).getroot()
                if root.tag == qname("xbrli:xbrl"):
                    return DocumentClass.XBRL_2_1
                if root.tag == qname("xhtml:html"):
                    return DocumentClass.IXBRL
            except etree.LxmlError:
                pass
        return None









