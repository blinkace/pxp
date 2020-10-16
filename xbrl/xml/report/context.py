from xbrl.model.report.period import InstantPeriod, DurationPeriod
from xbrl.xml.util import qname, childElements, childElement
from xbrl.const import NS
from xbrl.xbrlerror import XBRLError
from xbrl.qname import parseQName
from lxml import etree
import dateutil.parser
import dateutil.relativedelta

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
        entityElt = next(childElements(elt, 'xbrli', 'entity'))
        identifierElt = next(childElements(entityElt, 'xbrli', 'identifier'))
        scheme = identifierElt.get('scheme')
        identifier = identifierElt.text

        segmentContent = entityElt.xpath("xbrli:segment/*", namespaces = NS)

        scenarioContent = elt.xpath("xbrli:scenario/*", namespaces = NS)

        if len(segmentContent) > 0 and len(scenarioContent) > 0:
            raise XBRLError("xbrlxe:unexpectedContextContent", "Content found in both segment and scenario containers for context with ID '%s'" % cid)

        dimensions = dict()

        for e in segmentContent + scenarioContent:
            if e.tag == etree.QName(NS['xbrldi'], "explicitMember"):
                dimensions[e.get("dimension")] = parseQName(e.nsmap, e.text)
            elif e.tag == etree.QName(NS['xbrldi'], "typedMember"):
                raise ValueError("Typed dimensions not implemented")
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
        pe = childElement(contextElt, "xbrli", "period")
        instant = childElement(pe, "xbrli", "instant")
        start = childElement(pe, "xbrli", "startDate")
        end = childElement(pe, "xbrli", "endDate")
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
