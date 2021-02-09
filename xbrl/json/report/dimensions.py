from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from xbrl.model.report import ConceptCoreDimension, UnitCoreDimension, DurationPeriod, InstantPeriod, ExplicitTaxonomyDefinedDimensionValue, TypedTaxonomyDefinedDimensionValue, EntityCoreDimension, LanguageCoreDimension
from xbrl.model.taxonomy import TypedDimension
from xbrl.common.dimensions import getUnit, getConcept, getPeriod, getEntity, getLanguage

def getModelDimension(name, value, nsmap, taxonomy):
    if name == qname("xbrl:unit"):
        return getUnit(nsmap, value)
    if name == qname("xbrl:concept"):
        return getConcept(nsmap, taxonomy, value)
    if name == qname("xbrl:period"):
        return getPeriod(value)
    if name == qname("xbrl:entity"):
        return getEntity(nsmap, value)
    if name == qname("xbrl:language"):
        return getLanguage(value)
    dim = taxonomy.getDimension(name)
    if dim is None:
        raise XBRLError("oime:unknownDimension", "Dimension %s is not defined in taxonomy" % name)
    if isinstance(dim, TypedDimension):
        return TypedTaxonomyDefinedDimensionValue(name, value)
    else:
        return ExplicitTaxonomyDefinedDimensionValue(name, value)
