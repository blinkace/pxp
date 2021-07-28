from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from xbrl.model.report import ConceptCoreDimension, UnitCoreDimension, DurationPeriod, InstantPeriod, ExplicitTaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue, EntityCoreDimension, LanguageCoreDimension, NoteIdCoreDimension
from xbrl.model.taxonomy import TypedDimension
from xbrl.common.dimensions import getUnit, getConcept, getPeriod, getEntity, getLanguage
from xbrl.common import isValidQName

def getModelDimension(name, value, nsmap, taxonomy):
    if name == qname("xbrl:unit"):
        return getUnit(nsmap, value)
    if name == qname("xbrl:period"):
        return getPeriod(value)
    try:
        if name == qname("xbrl:concept"):
            return getConcept(nsmap, taxonomy, value)
        if name == qname("xbrl:entity"):
            return getEntity(nsmap, value)

    except XBRLError as e:
        if e.code in qnameset({"oimce"},{"invalidQName"}):
            raise XBRLError("xbrlje:invalidJSONStructure", e.message)
        raise e

    if name == qname("xbrl:language"):
        if value != value.lower():
            raise XBRLError("xbrlje:invalidLanguageCodeCase", "Language code '%s' is not expressed in lower-case form" % value)
        try:
            return getLanguage(value)
        except XBRLError as e:
            if e.code == qname("oime:invalidLanguage"):
                raise XBRLError("xbrlje:invalidJSONStructure", e.message)
            raise e

    if name == qname("xbrl:noteId"):
        return NoteIdCoreDimension(value)

    dim = taxonomy.getDimension(name)
    if dim is None:
        raise XBRLError("oime:unknownDimension", "Dimension %s is not defined in taxonomy" % name)
    if isinstance(dim, TypedDimension):
        return TypedTaxonomyDefinedDimensionValue(taxonomy, name, value)
    else:
        if not isValidQName(value):
            raise XBRLError("xbrlje:invalidDimensionValue", "Value '%s' for explicit dimension '%s' is not a valid QName" % (value, name))
            
        qname(value)
        return ExplicitTaxonomyDefinedDimensionValue(taxonomy, name, value)

