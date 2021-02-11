from .dimensions import Dimension

class TaxonomyDefinedDimensionValue(Dimension):

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    @property
    def asTuple(self):
        return (self.name, self.value)

    @property
    def dimension(self):
        return self.fact.report.taxonomy.getDimension(self.name)

class ExplicitTaxonomyDefinedDimensionValue(TaxonomyDefinedDimensionValue):

    @property
    def stringValue(self):
        return self.fact.report.asQName(self.value) 

class TypedTaxonomyDefinedDimensionValue(TaxonomyDefinedDimensionValue):

    @property
    def stringValue(self):
        return self.dimension.typedDomainDatatype.stringValue(self.value) if self.value is not None else None

