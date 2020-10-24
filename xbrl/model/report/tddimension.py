from .dimensions import Dimension

class TaxonomyDefinedDimension(Dimension):

    def __init__(self, dimension, value):
        super().__init__(dimension.name)
        self.dimension = dimension
        self.value = value

class ExplicitTaxonomyDefinedDimension(TaxonomyDefinedDimension):

    @property
    def stringValue(self):
        return self.fact.report.asQName(self.value.name)

class TypedTaxonomyDefinedDimension(TaxonomyDefinedDimension):

    @property
    def stringValue(self):
        return self.dimension.typedDomainDatatype.stringValue(self.value)

