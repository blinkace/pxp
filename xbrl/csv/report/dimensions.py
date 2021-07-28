from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from .period import parseCSVPeriodString
from .values import ExplicitNoValue
from xbrl.common import parseUnitString, parseSQName, InvalidSQName
from xbrl.model.report import UnitCoreDimension, DurationPeriod, InstantPeriod, ExplicitTaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue, EntityCoreDimension, LanguageCoreDimension
from xbrl.model.taxonomy import TypedDimension
from xbrl.common.validators import isValidQName
from xbrl.common.dimensions import getUnit, getConcept, getEntity, getLanguage, getExplicitDimensionValue
from xbrl.const import NS
import datetime

def getModelDimension(report, name, value):
    if name == qname("xbrl:unit"):
        return getUnit(report.nsmap, value)
    if name == qname("xbrl:concept"):
        if value is None:
            raise XBRLError("xbrlce:invalidConceptQName", "Concept dimension must not be nil")
        try:
            conceptDimension = getConcept(report.nsmap, report.taxonomy, value)
            if conceptDimension.concept.isAbstract:
                raise XBRLError("oime:valueForAbstractConcept", "%s is an abstract concept" % str(value))
            conceptDimension.concept.validateDatatype()
            return conceptDimension
        except XBRLError as e:
            if e.code == qname("oimce:invalidQName"):
                raise XBRLError("xbrlce:invalidConceptQName", e.message)
            raise e
    if name == qname("xbrl:period"):
        return getCSVPeriod(value)
    if name == qname("xbrl:entity"):
        return getEntity(report.nsmap, value)
    if name == qname("xbrl:language"):
        try:
            return getLanguage(value)
        except XBRLError as e:
            if e.code == qname("oime:invalidLanguage"):
                raise XBRLError("xbrlce:invalidLanguageCode", e.message)
            raise e
    dim = report.taxonomy.getDimension(name)
    if dim is None:
        raise XBRLError("oime:unknownDimension", "Dimension %s is not defined in taxonomy" % name)
    if isinstance(dim, TypedDimension):
        dv = TypedTaxonomyDefinedDimensionValue(report.taxonomy, name, value)
        dv.validateDatatype()
        return dv
    else:
        if not isValidQName(value):
            raise XBRLError("xbrlce:invalidDimensionValue", "Value '%s' for explicit dimension '%s' is not a valid QName" % (value, name))
        return getExplicitDimensionValue(report.nsmap, report.taxonomy, name, value)

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



