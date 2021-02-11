from .dimensions import ConceptCoreDimension
from .tddimension import TaxonomyDefinedDimensionValue
from .period import InstantPeriod, DurationPeriod
from xbrl.xml import qname
from xbrl.xbrlerror import XBRLError
from xbrl.const import LinkType
from xbrl.model.taxonomy import NoteConcept, PeriodType
from xbrl.common.period import fromISO
import decimal

class Fact:

    def __init__(self, factId, dimensions = set(), value = None, decimals = None, links = None):
        self.id = factId

        self.dimensions = dict()
        for d in dimensions:
            d.fact = self
            self.dimensions[d.name] = d

        self.value = value
        assert(decimals is None or type(decimals) == int)
        self.decimals = decimals
        self.report = None
        self.links = links if links is not None else {}

    def __repr__(self):
        dims = "; ".join("%s = %s" % (self.report.asQName(d.name), self.report.asQName(d.value.name)) for d in self.dimensions if isinstance(d, TaxonomyDefinedDimension))
        s = "%s[%s] = %s" % (self.report.asQName(self.concept.name), dims, self.value)

        return s

    @property
    def concept(self):
        return self.dimensions.get(qname("xbrl:concept")).concept

    @property
    def period(self):
        return self.dimensions.get(qname("xbrl:period"), None)

    @property
    def entity(self):
        return self.dimensions.get(qname("xbrl:entity"), None)

    def taxonomyDefinedDimensions(self):
        return (d for d in self.dimensions.values if isinstance(d, TaxonomyDefinedDimension))
        
    @property
    def isNumeric(self):
        return self.concept.isNumeric

    @property
    def stringValue(self):
        return self.concept.datatype.stringValue(self.value)

    @property
    def unit(self):
        return self.dimensions.get(qname("xbrl:unit"), None)

    @property
    def frozenDimensionSet(self):
        return frozenset(d.asTuple for d in self.dimensions.values())

    @property
    def numericValue(self):
        if not self.isNumeric:
            raise ValueError("Fact is not numeric")
        if self.concept.datatype.isDecimal:
            return decimal.Decimal(self.value)
        return float(self.value)

    
    @property
    def typedValue(self):
        """Return a value that supports a type-aware equality"""
        if self.value is None:
            return None
        if self.isNumeric:
            return self.numericValue
        return self.value

    @property
    def valueRange(self):
        val = decimal.Decimal(self.value)
        if self.decimals is None:
            return (val, val)
        r = decimal.Decimal(10)**(decimal.Decimal(self.decimals)*-1)
        return (val - r/2, val + r/2)

    @property
    def isNil(self):
        return self.value is None

    def validate(self):
        for linkType, linkGroups in self.links.items():
            for linkGroup, facts in linkGroups.items():
                for f in facts:
                    if linkType == LinkType.factFootnote and f.concept != NoteConcept:
                        raise XBRLError("oime:illegalStandardFootnoteTarget", "Fact '%s' is not a footnote fact.  fact-footnote relationships must have an xbrl:note fact as the target." % f.id)

        if self.concept.isAbstract:
            raise XBRLError("oime:valueForAbstractConcept", "Fact '%s' is reported for an abstract concept ('%s')" % (self.id, str(self.concept.name)))

        if self.concept.periodType == PeriodType.DURATION:
            if self.period is not None and not isinstance(self.period, DurationPeriod):
                raise XBRLError("oime:invalidPeriodDimension", "Fact '%s' has a duration concept but an instant period '%s'" % (self.id, self.period))
        else:
            if self.period is None:
                raise XBRLError("oime:missingPeriodDimension", "Fact '%s' has an instant concept but no period dimension" % self.id)
            elif not isinstance(self.period, InstantPeriod):
                raise XBRLError("oime:invalidPeriodDimension", "Fact '%s' has an instant concept but a duration period" % self.id)
        if not self.isNumeric and self.decimals is not None:
            raise XBRLError("oime:misplacedDecimalsProperty", "Fact '%s' has decimals specified but is not numeric" % self.id)



    def isEqual(self, other):
        return self.frozenDimensionSet == other.frozenDimensionSet and self.typedValue == other.typedValue and self.id == other.id

