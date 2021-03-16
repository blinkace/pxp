from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from .period import parseCSVPeriodString
from .values import ExplicitNoValue
from xbrl.common import parseUnitString, parseSQName, InvalidSQName
from xbrl.model.report import ConceptCoreDimension, UnitCoreDimension, DurationPeriod, InstantPeriod, ExplicitTaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue, EntityCoreDimension, LanguageCoreDimension
from xbrl.model.taxonomy import TypedDimension
from xbrl.common.validators import isValidQName
from xbrl.common.dimensions import getUnit, getConcept, getEntity, getLanguage
from xbrl.const import NS
import datetime

def getModelDimension(report, name, value):
    if name == qname("xbrl:unit"):
        return getUnit(report.nsmap, value)
    if name == qname("xbrl:concept"):
        if value is None:
            raise XBRLError("xbrlce:invalidJSONStructure", "Concept dimension must not be nil")
        try:
            return getConcept(report.nsmap, report.taxonomy, value)
        except XBRLError as e:
            if e.code == qname("oimce:invalidQName"):
                raise XBRLError("xbrlce:invalidConceptQName", e.message)
            raise e
    if name == qname("xbrl:period"):
        return getCSVPeriod(value)
    if name == qname("xbrl:entity"):
        try:
            return getEntity(report.nsmap, value)
        except XBRLError as e:
            if e.code == qname("oimce:invalidSQName"):
                raise XBRLError("xbrlce:invalidSQName", e.message)
            raise e
    if name == qname("xbrl:language"):
        return getLanguage(value)
    dim = report.taxonomy.getDimension(name)
    if dim is None:
        raise XBRLError("oime:unknownDimension", "Dimension %s is not defined in taxonomy" % name)
    if isinstance(dim, TypedDimension):
        return TypedTaxonomyDefinedDimensionValue(name, value)
    else:
        return ExplicitTaxonomyDefinedDimensionValue(name, qname(value, report.nsmap))

def getCSVPeriod(period):
    # #nil or JSON null
    if period is None:
        raise XBRLError("xbrlce:invalidPeriodRepresentation", "nil is not a valid period value")

    if isinstance(period, datetime.datetime):
        # Was obtained as the target of a parameter reference with period specifier, and has already been converted to datetime
        return InstantPeriod(period)
    else:
        p = parseCSVPeriodString(period)
        if p[1] is None:
            return InstantPeriod(p[0])
        else:
            return DurationPeriod(p[0], p[1])



