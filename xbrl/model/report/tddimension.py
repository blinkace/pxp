from .dimensions import Dimension

class TaxonomyDefinedDimension(Dimension):

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    @property
    def asTuple(self):
        return (self.name, self.value)

class ExplicitTaxonomyDefinedDimension(TaxonomyDefinedDimension):

    @property
    def stringValue(self):
        return self.fact.report.asQName(self.value.name)

class TypedTaxonomyDefinedDimension(TaxonomyDefinedDimension):

    @property
    def stringValue(self):
        return self.dimension.typedDomainDatatype.stringValue(self.value)

