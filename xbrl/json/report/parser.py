import json
import logging
import os
from xbrl.json.schema import json_validate, DuplicateKeyError
from xbrl.const import DocumentType, NS, OIM_COMMON_RESERVED_PREFIX_MAP, LINK_RESERVED_URI_MAP
from xbrl.xml import qname
from xbrl.xbrlerror import XBRLError
from xbrl.common.validators import validateURIMap, isValidQName, isValidAnyURI, isCanonicalAnyURI
from xbrl.model.report import Report, Fact
from xbrl.xml.taxonomy.document import SchemaRef
from urllib.parse import urljoin, urlparse
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
        linkGroups = docInfo.get("linkGroups", {})
        linkTypes = docInfo.get("linkTypes", {})
        try:
            validateURIMap(nsmap, reservedPrefixMap = OIM_COMMON_RESERVED_PREFIX_MAP)
            validateURIMap(linkGroups, reservedPrefixMap = LINK_RESERVED_URI_MAP)
            validateURIMap(linkTypes, reservedPrefixMap = LINK_RESERVED_URI_MAP)
        except XBRLError as e:
            e.reraise({qname("oimce:invalidStructure"): qname("xbrlje:invalidJSONStructure")})


        baseURL = docInfo.get("baseURL", None)
        if baseURL is not None:
            if not(isValidAnyURI(baseURL)):
                raise XBRLError("xbrlje:invalidJSONStructure", "'%s' is not a valid URL" % baseURL)
            if not(isCanonicalAnyURI(baseURL)):
                raise XBRLError("xbrlje:invalidJSONStructure", "'%s' is not in canonical form" % baseURL)


        taxonomy = self.getTaxonomy(docInfo, url)

        modelReport = Report(taxonomy)
        
        for fid, fact in j.get("facts", {}).items():
            factDims = dict()
            for dimname, dimval in fact.get("dimensions", {}).items():
                dimqname = qname(dimname, { **nsmap, None: NS.xbrl })
                factDims[dimqname] = getModelDimension(dimqname, dimval, nsmap, taxonomy)
            v = fact.get("value", None)
            f = Fact(
                factId = fid,
                dimensions = factDims.values(),
                value = v,
                decimals = fact.get("decimals", None)
            )
            if docInfo.get("features", {}).get("xbrl:canonicalValues", False):
                if f.concept.datatype.canonicalValue(v) != v:
                    raise XBRLError("xbrlje:nonCanonicalValue", "'%s' is not in canonical form (should be '%s')" % (v, f.concept.datatype.canonicalValue(v)))



            modelReport.addFact(f)

        modelReport.validate()
        features = docInfo.get("features", {})
        for name in features.keys():
            qname(name, nsmap = { **nsmap })
        allowedDuplicates = features.get("xbrl:allowedDuplicates", "all")
        self.validateDuplicates(modelReport, allowedDuplicates)
        return modelReport

    def validateDuplicates(self, report, mode):
        if mode == 'none':
            report.validateDuplicatesAllowNone()
        elif mode == 'complete':
            report.validateDuplicatesAllowComplete()
        elif mode == 'consistent':
            report.validateDuplicatesAllowConsistent()



    def getTaxonomy(self, docInfo, url):
        taxonomy = docInfo.get("taxonomy", [])
        if len(taxonomy) == 0:
            raise XBRLError("oime:noTaxonomy", "No taxonomy specified in metadata")

        schemaRefs = list(SchemaRef(urljoin(url, t)) for t in taxonomy)
        return self.processor.loadTaxonomy(schemaRefs)
