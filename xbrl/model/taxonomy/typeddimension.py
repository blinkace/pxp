from .concept import Concept

class TypedDimension(Concept):

    def __init__(self, name, datatype, substitutionGroupChain, typedDomainDatatype, periodType):
        super().__init__(name, datatype, substitutionGroupChain, periodType)
        self.typedDomainDatatype = typedDomainDatatype
