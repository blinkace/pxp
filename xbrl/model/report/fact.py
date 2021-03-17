from .dimensions import ConceptCoreDimension
from .tddimension import TaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue
from .period import InstantPeriod, DurationPeriod
from xbrl.xml import qname
from xbrl.xbrlerror import XBRLError
from xbrl.const import LinkType
from xbrl.model.taxonomy import NoteConcept, PeriodType, ListBasedDatatype, ComplexDatatype
from xbrl.common.period import DateTimeUnion
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
        dimStrs = []
        for d in self.dimensions.values():
            if isinstance(d, TaxonomyDefinedDimensionValue):
                dimStrs.append("%s = %s" % (self.report.asQName(d.name), d.stringValue))
            else:
                dimStrs.append("%s = %s" % (d.name.localname, d.stringValue))


        dims = "; ".join(dimStrs)
        s = "%s[%s] = %s (#%s)" % (self.report.asQName(self.concept.name), dims, self.value, self.id)

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
        return (d for d in self.dimensions.values() if isinstance(d, TaxonomyDefinedDimensionValue))
        
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
        if self.concept.isDateTime:
            return DateTimeUnion(self.value)

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

    @property
    def isText(self):
        return self.concept.datatype.isText

    def validate(self):
        for linkType, linkGroups in self.links.items():
            for linkGroup, facts in linkGroups.items():
                for f in facts:
                    if linkType == LinkType.footnote and f.concept != NoteConcept:
                        raise XBRLError("oime:illegalStandardFootnoteTarget", "Fact '%s' is not a footnote fact.  fact-footnote relationships must have an xbrl:note fact as the target." % f.id)

        if self.concept.isAbstract:
            raise XBRLError("oime:valueForAbstractConcept", "Fact '%s' is reported for an abstract concept ('%s')" % (self.id, str(self.concept.name)))

        if self.value is None and not self.concept.nillable:
            raise XBRLError("oime:invalidFactValue", "Fact '%s' has nill value by concept %s is not nillable" % (self.id, str(self.concept.name)))

        if self.concept.periodType == PeriodType.DURATION:
            if self.period is not None and not isinstance(self.period, DurationPeriod):
                raise XBRLError("oime:invalidPeriodDimension", "Fact '%s' has a duration concept but an instant period '%s'" % (self.id, self.period.stringValue))
        else:
            if self.period is None:
                raise XBRLError("oime:missingPeriodDimension", "Fact '%s' has an instant concept but no period dimension" % self.id)
            elif not isinstance(self.period, InstantPeriod):
                raise XBRLError("oime:invalidPeriodDimension", "Fact '%s' has an instant concept but a duration period" % self.id)
        if not self.isNumeric and self.decimals is not None:
            raise XBRLError("oime:misplacedDecimalsProperty", "Fact '%s' has decimals specified but is not numeric" % self.id)

        if not self.isNumeric and qname("xbrl:unit") in self.dimensions:
            raise XBRLError("oime:misplacedUnitDimension", "Fact '%s' has units specified but is not numeric" % self.id)

        if not self.isText and qname("xbrl:language") in self.dimensions:
            raise XBRLError("oime:misplacedLanguageDimension", "Fact '%s' has language specified but is not a text fact" % self.id)


        self.validateNoteFact()
        self.validateTypedDimensionDatatypes()

    def validateNoteFact(self):
        if self.concept.name == qname('xbrl:note'):
            noteIdDim = self.dimensions.get(qname("xbrl:noteId"))
            if noteIdDim is None:
                raise XBRLError("oime:missingNoteIDDimension", "Note fact '%s' does not have the noteId dimension" % (self.id))
            if noteIdDim.noteId != self.id:
                raise XBRLError("oime:invalidNoteIDValue", "Note fact '%s' has noteId dimension '%s' which does not match fact ID '%s'" % (self.id, noteIdDim.noteId, self.id))
            if qname("xbrl:language") not in self.dimensions:
                raise XBRLError("oime:missingLanguageForNoteFact", "Note fact '%s' does not have the language core dimension" % (self.id))
            if qname("xbrl:entity") in self.dimensions:
                raise XBRLError("oime:misplacedNoteFactDimension", "Note fact '%s' has misplaced entity dimension" % (self.id))
            if qname("xbrl:period") in self.dimensions:
                raise XBRLError("oime:misplacedNoteFactDimension", "Note fact '%s' has misplaced period dimension" % (self.id))
            if next(self.taxonomyDefinedDimensions(), None) is not None:
                raise XBRLError("oime:misplacedNoteFactDimension", "Note fact '%s' has misplaced taxonomy-defined dimensions" % (self.id))
            if next((src 
                for linkGroups in self.report.inboundLinks(self).values()
                    for srcs in linkGroups.values()
                        for src in srcs), None) is None:
                raise XBRLError("oime:unusedNoteFact", "Note fact '%s' is not referenced by any links" % (self.id))

        else:
            if qname("xbrl:noteId") in self.dimensions:
                raise XBRLError("oime:misplacedNoteIDDimension", "Fact '%s' has a xbrl:noteId dimension but has concept %s not xbrl:note" % (self.id, str(self.concept.name)))



    def validateTypedDimensionDatatypes(self):
        for dimname, dimvalue in self.dimensions.items():
            if isinstance(dimvalue, TypedTaxonomyDefinedDimensionValue):
                if dimvalue.datatype.isLegacy:
                    raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' on fact '%s' has a datatype which is, or is derived from an unsupported legacy datatype" % (str(dimname), self.id))
            
                if isinstance(dimvalue.datatype, ListBasedDatatype):
                    raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' on fact '%s' is derived by list" % (str(dimname), self.id))

                if isinstance(dimvalue.datatype, ComplexDatatype):
                    raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' on fact '%s' is complex" % (str(dimname), self.id))

    def isEqual(self, other, checkId = True):
        return self.frozenDimensionSet == other.frozenDimensionSet and self.typedValue == other.typedValue and (self.id == other.id or not checkId)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

