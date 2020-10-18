from .dimensions import ConceptCoreDimension
from .tddimension import TaxonomyDefinedDimension

class Fact:

    def __init__(self, factId, dimensions = set(), value = None, decimals = None):
        self.id = factId
        self.dimensions = dimensions
        self.value = value
        self.decimals = None
        self.report = None

    def __repr__(self):
        dims = "; ".join("%s = %s" % (self.report.taxonomy.asQName(d.dimension.name), self.report.taxonomy.asQName(d.value.name)) for d in self.dimensions if isinstance(d, TaxonomyDefinedDimension))
        s = "%s[%s] = %s" % (self.report.taxonomy.asQName(self.concept.name), dims, self.value)

        return s

    @property
    def concept(self):
        return next(d.concept for d in self.dimensions if isinstance(d, ConceptCoreDimension))

    def taxonomyDefinedDimensions(self):
        return (d for d in self.dimensions if isinstance(d, TaxonomyDefinedDimension))

        
