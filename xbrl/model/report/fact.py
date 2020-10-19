from .dimensions import ConceptCoreDimension
from .tddimension import TaxonomyDefinedDimension

class Fact:

    def __init__(self, factId, dimensions = set(), value = None, decimals = None):
        self.id = factId
        self.dimensions = dimensions
        for d in self.dimensions:
            d.fact = self
        self.value = value
        self.decimals = decimals
        self.report = None

    def __repr__(self):
        dims = "; ".join("%s = %s" % (self.report.asQName(d.name), self.report.asQName(d.value.name)) for d in self.dimensions if isinstance(d, TaxonomyDefinedDimension))
        s = "%s[%s] = %s" % (self.report.asQName(self.concept.name), dims, self.value)

        return s

    @property
    def concept(self):
        return next(d.concept for d in self.dimensions if isinstance(d, ConceptCoreDimension))

    def taxonomyDefinedDimensions(self):
        return (d for d in self.dimensions if isinstance(d, TaxonomyDefinedDimension))
        
    @property
    def isNumeric(self):
        return self.concept.isNumeric
