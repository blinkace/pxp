from lxml import etree
from xbrl.const import NS
from xbrl.document import SchemaRef
from xbrl.documentloader import DocumentLoader
from xbrl.xml import qname, parser
from xbrl.xbrlerror import XBRLError
from math import log10, fabs, floor
import xbrl.model.report as report 

from .context import Context
from .unit import Unit
from urllib.parse import urljoin

class XBRLReportParser:

    def __init__(self, processor):
        self.processor = processor
        self.idCount = 0
        self.contexts = dict()
        self.units = dict()


    def parse(self, url):
        with self.processor.resolver.open(url) as src:
            tree = etree.parse(src, parser())
        root = tree.getroot()
        self.url = url
        self.parseContexts(root)
        self.parseUnits(root)
        self.taxonomy = self.getTaxonomy(root)
        return self.parseFacts(root)


    def parseContexts(self, root):
        for ce in root.childElements(qname('xbrli:context')):
            c = Context.from_xml(ce)
            self.contexts[c.id] = c

    def parseUnits(self, root):
        for ue in root.childElements(qname('xbrli:unit')):
            u = Unit.from_xml(ue)
            self.units[u.id] = u

    def generateId(self):
        self.idCount = self.idCount + 1
        return "f%d" % self.idCount

    def parseFacts(self, root):
        rpt = report.Report(self.taxonomy)
        for e in root:
            name = etree.QName(e.tag)
            if name.namespace in (NS.xbrli, NS.link):
                continue;

            concept = self.taxonomy.concepts.get(name, None)
            if concept is None:
                raise XBRLError("oime:missingConceptDefinition", "Could not find concept definition for %s" % name.text)

            dims = set()
            dims.add(report.ConceptCoreDimension(concept))

            cid = e.get("contextRef")
            ctxt = self.contexts.get(cid, None)
            if ctxt is None:
                raise XBRLError("xbrl21e:missingContext", "No context with ID '%s'" % cid)

            dims.update(ctxt.asDimensions(self.taxonomy))

            uid = e.get("unitRef", None)
            if uid is not None:
                unit = self.units.get(uid, None)
                if unit is None:
                    raise XBRLError("xbrl21e:missingUnit", "No unit with ID '%s'" % cid)
                dims.update(unit.asDimensions())

            f = report.Fact(e.get("id", self.generateId()), dimensions = dims, value = e.text, decimals = self.parseDecimals(e))
            rpt.addFact(f)
        return rpt

    def parseDecimals(self, fact):
        d = fact.get("decimals", None)
        if d is None:
            p = fact.get("precision", None)
            if p is None or p == "INF":
                return None

            precision = int(p)
            if precision == 0:
                raise XBRLError("xbrl21e:invalidPrecision", "precision = 0 not supported")
            value = float(fact.text)
            if value == 0:
                return XBRLError("xbrl21e:invalidPrecision", "precision for a value of 0 is meaningless")
            else:
                return precision - int(floor(log10(fabs(value)))) - 1

        if d == "INF":
            return None
        return int(d)

    def getTaxonomy(self, root):
        schemaRefs = list(SchemaRef(urljoin(self.url, e.get(qname("xlink:href")))) 
            for e in root.childElements(qname('link:schemaRef')))
        dl = DocumentLoader(url_resolver = self.processor.resolver)
        dts = dl.load(schemaRefs)
        return dts.buildTaxonomy()

