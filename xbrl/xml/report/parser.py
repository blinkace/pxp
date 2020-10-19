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


    def parse(self, url):
        with self.processor.resolver.open(url) as src:
            tree = etree.parse(src, parser())
        root = tree.getroot()
        self.contexts = self.parseContexts(root)
        self.units = self.parseUnits(root)
        self.taxonomy = self.getTaxonomy(root, url)
        return self.parseFacts(root)


    def parseContexts(self, root):
        contexts = dict()
        for ce in root.childElements(qname('xbrli:context')):
            c = Context.from_xml(ce)
            contexts[c.id] = c
        return contexts

    def parseUnits(self, root):
        units = dict()
        for ue in root.childElements(qname('xbrli:unit')):
            u = Unit.from_xml(ue)
            units[u.id] = u
        return units

    def generateId(self):
        self.idCount = self.idCount + 1
        return "f%d" % self.idCount

    def parseFacts(self, root):
        rpt = report.Report(self.taxonomy)
        for e in root:
            name = etree.QName(e.tag)
            if name.namespace in (NS['xbrli'], NS['link']):
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

            dims.add(ctxt.period)

            for dim, dval in ctxt.dimensions.items():
                dimconcept = self.taxonomy.concepts.get(dim, None)
                if dimconcept is None:
                    raise XBRLError("xbrldie:ExplicitMemberNotExplicitDimensionError", "Could not find definition for dimension %s" % dim)
                if not dimconcept.isDimension:
                    raise XBRLError("xbrldie:ExplicitMemberNotExplicitDimensionError", "Concept %s is not a dimension" % dim)
                valconcept = self.taxonomy.concepts.get(dval, None)
                if valconcept is None:
                    raise XBRLError("xbrldie:ExplicitMemberUndefinedQNameError", "Could not find member for dimension value %s" % dval)

                dims.add(report.ExplicitTaxonomyDefinedDimension(dimconcept, valconcept))

            dims.add(report.EntityCoreDimension(ctxt.scheme, ctxt.identifier))

            uid = e.get("unitRef", None)
            if uid is not None:
                unit = self.units.get(uid, None)
                if unit is None:
                    raise XBRLError("xbrl21e:missingUnit", "No unit with ID '%s'" % cid)
                if not unit.isPure:
                    dims.add(report.UnitCoreDimension(unit.numerators, unit.denominators))

            decimals = self.parseDecimals(e)

            f = report.Fact(e.get("id", self.generateId()), dimensions = dims, value = e.text, decimals = decimals)
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

    def getTaxonomy(self, root, url):
        schemaRefs = list(SchemaRef(urljoin(url, e.get(etree.QName(NS['xlink'],"href")))) 
            for e in root.childElements(qname('link:schemaRef')))
        dl = DocumentLoader(url_resolver = self.processor.resolver)
        dts = dl.load(schemaRefs)
        return dts.buildTaxonomy()

