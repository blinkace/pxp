from .concept import Concept

class TypedDimension(Concept):

    def __init__(self, name, datatype, substitutionGroupChain, typedDomainDatatype):
        super().__init__(name, datatype, substitutionGroupChain)
        self.typedDomainDatatype = typedDomainDatatype
