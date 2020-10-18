from lxml import etree
from xbrl.const import NS
from xbrl.document import SchemaRef
from xbrl.documentloader import DocumentLoader
from xbrl.xml.util import qname, childElements, childElement
from xbrl.xbrlerror import XBRLError
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
            tree = etree.parse(src)
        root = tree.getroot()
        self.contexts = self.parseContexts(root)
        self.units = self.parseUnits(root)
        self.taxonomy = self.getTaxonomy(root, url)
        return self.parseFacts(root)


    def parseContexts(self, root):
        contexts = dict()
        for ce in childElements(root, 'xbrli', 'context'):
            c = Context.from_xml(ce)
            contexts[c.id] = c
        return contexts

    def parseUnits(self, root):
        units = dict()
        for ue in childElements(root, 'xbrli', 'unit'):
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
                raise XBRLError("missingContext", "No context with ID '%s'" % cid)
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
                    raise XBRLError("missingUnit", "No unit with ID '%s'" % cid)


            f = report.Fact(e.get("id", self.generateId()), dimensions = dims, value = e.text)
            rpt.addFact(f)
            print(f)
            #print("%s (%s) = %s" % (name.text, concept.itemType.text, e.text))
        return rpt

            

    def getTaxonomy(self, root, url):
        schemaRefs = list(SchemaRef(urljoin(url, e.get(etree.QName(NS['xlink'],"href")))) 
            for e in childElements(root, 'link', 'schemaRef'))
        dl = DocumentLoader(url_resolver = self.processor.resolver)
        dts = dl.load(schemaRefs)
        return dts.buildTaxonomy()

