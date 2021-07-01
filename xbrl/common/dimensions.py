from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from xbrl.common import parseUnitString, parseSQName, InvalidSQName
from xbrl.model.report import ConceptCoreDimension, UnitCoreDimension, DurationPeriod, InstantPeriod, ExplicitTaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue, EntityCoreDimension, LanguageCoreDimension
from xbrl.model.taxonomy import TypedDimension
from xbrl.common.validators import isValidQName
from xbrl.common.language import isValidLanguageCode
from xbrl.const import NS
from .period import parsePeriodString
import datetime

def getUnit(nsmap, unit):
    (nums, denoms) = parseUnitString(unit, nsmap)
    if nums == [ qname("xbrli:pure") ] and denoms == []:
        raise XBRLError("oime:illegalPureUnit", "Pure units must not be specified explicitly")
    return UnitCoreDimension(nums, denoms)

def getConcept(nsmap, taxonomy, conceptNameStr):
    if not isValidQName(conceptNameStr):
        raise XBRLError("oimce:invalidQName", "'%s' is not a valid QName" % conceptNameStr)

    conceptName = qname(conceptNameStr, { "xbrl": NS.xbrl, **nsmap})

    concept = taxonomy.concepts.get(conceptName)
    if concept is None:
        raise XBRLError("oime:unknownConcept", "Concept %s not found in taxonomy" % str(conceptName))

    return ConceptCoreDimension(concept)

def getPeriod(period):
    if period is None:
        raise XBRLError("xbrlce:invalidPeriodRepresentation", "nil is not a valid period value")
    (start, end) = parsePeriodString(period)
    if end is None:
        return InstantPeriod(start)
    else:
        return DurationPeriod(start, end)



def getEntity(nsmap, entityStr):
    # oimce:invalidSQName isn't actually defined by the spec.  The CSV and JSON
    # code will catch and conver this to a different code.
    if entityStr is None:
        raise XBRLError("oimce:invalidSQName", "Entity dimension must not be nil")

    try:
        (scheme, identifier) = parseSQName(entityStr, nsmap)
    except InvalidSQName as e:
        raise XBRLError("oimce:invalidSQName", str(e))

    if scheme in [NS.entities, NS.entities_cr7] and identifier == 'NA':
        raise XBRLError("oime:invalidUseOfReservedIdentifier", "The reserved entity identifier {%s}%s must not be used" % (scheme, identifier))

    return EntityCoreDimension(scheme, identifier)

def getLanguage(langstr):
    if not isValidLanguageCode(langstr):
        raise XBRLError("oime:invalidLanguage", "'%s' is not a valid language code" % langstr)
    return LanguageCoreDimension(langstr)
