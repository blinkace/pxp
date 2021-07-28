from xbrl.const import NS
from xbrl.xml import qname
from xbrl.common import sqname
from xbrl.xbrlerror import XBRLError
from .datatype import Datatype, ComplexDatatype
from enum import Enum, auto

class PeriodType(Enum):
    INSTANT = auto()
    DURATION = auto()

class Concept:

    def __init__(self, name, datatype, substitutionGroupChain, periodType, isAbstract = False, nillable = False):
        self.name = name
        self.datatype = datatype
        self.substitutionGroupChain = substitutionGroupChain
        self.periodType = periodType
        self.isAbstract = isAbstract
        self.nillable = nillable

    @property
    def itemType(self):
        return datatype.itemType

    @property
    def isNumeric(self):
        return self.datatype.isNumeric

    @property
    def isDateTime(self):
        return self.datatype.isDateTime

    @property
    def isText(self):
        return self.datatype.isText

    @property
    def isLanguageType(self):
        return self.datatype.isLanguage

    @property
    def isEnumeration(self):
        return self.datatype.isEnumeration
    
    @property
    def isEnumerationSet(self):
        return self.datatype.isEnumerationSet

    @property
    def isDimension(self):
        return qname("xbrldt:dimensionItem") in self.substitutionGroupChain

    def validateDatatype(self):
        if self.datatype.isFraction:
            raise XBRLError("oime:unsupportedConceptDataType", "Concept '%s' has unsupported fractionItemType" % self.name)
        if self.datatype.isPrefixedContent:
            raise XBRLError("oime:unsupportedConceptDataType", "Concept '%s' has unsupported prefixed content type" % self.name)
        if isinstance(self.datatype, ComplexDatatype):
            raise XBRLError("oime:unsupportedConceptDataType", "Concept '%s' has a datatype with complex content" % self.name)

    def __eq__(self, other):
        return self.name == other.name

def NoteConcept():
    return Concept(qname("xbrl:note"), Datatype([sqname("xs:string")]), [ qname("xbrli:item") ], PeriodType.DURATION)
