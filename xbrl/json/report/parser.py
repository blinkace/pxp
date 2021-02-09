import json
import logging
import os
from xbrl.json.schema import json_validate, DuplicateKeyError
from xbrl.const import DocumentType, NS
from xbrl.xml import qname
from xbrl.xbrlerror import XBRLError
from xbrl.common.validators import validateURIMap, isValidQName
from xbrl.model.report import Report, Fact
from xbrl.xml.taxonomy.document import SchemaRef
from urllib.parse import urljoin
from .dimensions import getModelDimension

logger = logging.getLogger(__name__)

class XBRLJSONReportParser:

    def __init__(self, processor):
        self.processor = processor

    def parse(self, url):

        # Make sure we raise unsupportedDocumentType rather than
        # invalidJSONStructure if documentType is not present.
        try:
            with self.processor.resolver.open(url) as src:
                jsonStr = src.read().decode("utf-8") 
                j = json.loads(jsonStr)
        except UnicodeDecodeError as e:
            raise XBRLError("xbrlje:invalidJSON", "Unicode decode error loading %s: %s" % (src, str(e)))
        except json.JSONDecodeError as e:
            raise XBRLError("xbrlje:invalidJSON", "JSON decode error %s: %s" % (src, str(e)))

        docInfo = j.get("documentInfo",{})
        docType = docInfo.get("documentType", None) if type(docInfo) == dict else None
        if type(docType) != str or docType not in {DocumentType.xbrljson_git, DocumentType.xbrljson_wgwd}:
            raise XBRLError("oimce:unsupportedDocumentType", "Unsupported document type: %s" % docType)

        with self.processor.resolver.open(url) as src:
            try:
                err = json_validate(os.path.join(os.path.dirname(__file__), "xbrl-json-schema.json"), src)
            except DuplicateKeyError as e:
                raise XBRLError("xbrlje:invalidJSON", str(e))
        if err is not None:
            raise XBRLError("xbrlje:invalidJSONStructure", err)

        nsmap = docInfo.get("namespaces", {})
        validateURIMap(nsmap)

        taxonomy = self.getTaxonomy(docInfo, url)

        modelReport = Report(taxonomy)
        
        for fid, fact in j.get("facts", {}).items():
            factDims = dict()
            for dimname, dimval in fact.get("dimensions", {}).items():
                dimqname = qname(dimname, { **nsmap, None: NS.xbrl })
                factDims[dimqname] = getModelDimension(dimqname, dimval, nsmap, taxonomy)

            modelReport.addFact(Fact(
                factId = fid,
                dimensions = factDims.values(),
                value = fact.get("value", None),
                decimals = fact.get("decimals", None)
                ))

        modelReport.validate()
        return modelReport


    def getTaxonomy(self, docInfo, url):
        taxonomy = docInfo.get("taxonomy", [])
        if len(taxonomy) == 0:
            raise XBRLError("oime:noTaxonomy", "No taxonomy specified in metadata")

        schemaRefs = list(SchemaRef(urljoin(url, t)) for t in taxonomy)
        return self.processor.loadTaxonomy(schemaRefs)
