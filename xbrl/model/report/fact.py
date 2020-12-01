from .dimensions import ConceptCoreDimension
from .tddimension import TaxonomyDefinedDimension
from xbrl.xml import qname

class Fact:

    def __init__(self, factId, dimensions = set(), value = None, decimals = None, links = None):
        self.id = factId

        self.dimensions = dict()
        for d in dimensions:
            d.fact = self
            self.dimensions[d.name] = d

        self.value = value
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
