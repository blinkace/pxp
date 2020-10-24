from xbrl.model.report.period import InstantPeriod, DurationPeriod
from xbrl.xml.util import qname
from xbrl.const import NSMAP
from xbrl.xbrlerror import XBRLError
from lxml import etree
import dateutil.parser
import dateutil.relativedelta
import logging
import xbrl.model.report as report 
from xbrl.model.taxonomy import TypedDimension

class Context:

    def __init__(self, cid, scheme, identifier, period, dimensions):
        self.scheme = scheme
        self.identifier = identifier
        self.period = period
        self.dimensions = dimensions
        self.id = cid

    def __repr__(self):
        s = "Entity: {%s}%s\n" % (self.scheme, self.identifier)
        if isinstance(self.period, InstantPeriod):
            s += "Instant: %s\n" % (self.period.instant)
        elif isinstance(self.period, DurationPeriod):
            s += "Duration: %s/%s" % (self.period.start, self.period.end)

        return s

    @classmethod
    def from_xml(cls, elt):
        cid = elt.get('id')
        entityElt = elt.childElement(qname('xbrli:entity'))
        identifierElt = entityElt.childElement(qname('xbrli:identifier'))

        scheme = identifierElt.get('scheme')
        identifier = identifierElt.text

        segmentContent = entityElt.xpath("xbrli:segment/*", namespaces = NSMAP)

        scenarioContent = elt.xpath("xbrli:scenario/*", namespaces = NSMAP)

        if len(segmentContent) > 0 and len(scenarioContent) > 0:
            raise XBRLError("xbrlxe:unexpectedContextContent", "Content found in both segment and scenario containers for context with ID '%s'" % cid)

        dimensions = dict()

        for e in segmentContent + scenarioContent:
            if e.tag == qname("xbrldi:explicitMember"):
                dimensions[e.qnameAttrValue("dimension")] = e.qnameValue
            elif e.tag == qname("xbrldi:typedMember"):
                name = e.qnameAttrValue("dimension")
                typedDimElts = list(e.childElements())
                if len(typedDimElts) != 1:
                    raise XBRLError("invalidTypedMember", "xbrldi:typedMember element did not have exactly one child")
                typedDimElt = typedDimElts[0]
                if len(list(typedDimElt.childElements())) != 0:
                    raise XBRLError("xbrlxe:unsupportedComplexTypedDimension", "Complex typed dimensions are not supported (%s)" % (name))

                # XXX need to check for QName type
                dimensions[e.qnameAttrValue("dimension")] = typedDimElt.text

            else:
                raise XBRLError("xbrlxe:nonDimensionalSegmentScenarioContent", "Non-dimensional content found in context '%s': %s" % (cid, e.tag))

        period = Context.parse_period(elt)
        
        return cls(
                cid = cid,
                scheme = scheme,
                identifier = identifier,
                period = period,
                dimensions = dimensions)

    def parse_period(contextElt):
        pe = contextElt.childElement(qname("xbrli:period"))
        instant = pe.childElement(qname("xbrli:instant"))
        start = pe.childElement(qname("xbrli:startDate"))
        end = pe.childElement(qname("xbrli:endDate"))
        if instant is not None:
            period = InstantPeriod(Context.parseDateTimeDateUnion(instant.text))
        else:
            period = DurationPeriod(
                Context.parseDateTimeDateUnion(start.text, defaultToEndOfDay = False),
                Context.parseDateTimeDateUnion(end.text)
            )

        return period

    def parseDateTimeDateUnion(dtdu, defaultToEndOfDay = True):
        t = dateutil.parser.parse(dtdu)
        if "T" not in dtdu and defaultToEndOfDay:
            t = t + dateutil.relativedelta.relativedelta(days = 1)
        return t

    def asDimensions(self, taxonomy):
        dims = set()

        dims.add(self.period)

        for dim, dval in self.dimensions.items():
            dimconcept = taxonomy.concepts.get(dim, None)
            # XXX Wrong error codes for typed dimensions
            if dimconcept is None:
                raise XBRLError("xbrldie:ExplicitMemberNotExplicitDimensionError", "Could not find definition for dimension %s" % dim)
            if not dimconcept.isDimension:
                raise XBRLError("xbrldie:ExplicitMemberNotExplicitDimensionError", "Concept %s is not a dimension" % dim)
            if isinstance(dimconcept,TypedDimension):
                dims.add(report.TypedTaxonomyDefinedDimension(dimconcept, dval))
            else:
                valconcept = taxonomy.concepts.get(dval, None)
                if valconcept is None:
                    raise XBRLError("xbrldie:ExplicitMemberUndefinedQNameError", "Could not find member for dimension value %s" % dval)
                dims.add(report.ExplicitTaxonomyDefinedDimension(dimconcept, valconcept))

        dims.add(report.EntityCoreDimension(self.scheme, self.identifier))

        return dims
