from .dimensions import Dimension
from xbrl.model.taxonomy import ListBasedDatatype, ComplexDatatype, UnionBasedDatatype
from xbrl.xbrlerror import XBRLError

class TaxonomyDefinedDimensionValue(Dimension):

    def __init__(self, taxonomy, name, value):
        super().__init__(name)
        self.value = value
        self.taxonomy = taxonomy

    @property
    def asTuple(self):
        return (self.name, self.value)

    @property
    def dimension(self):
        return self.taxonomy.getDimension(self.name)

class ExplicitTaxonomyDefinedDimensionValue(TaxonomyDefinedDimensionValue):

    # Value should be a model.taxonomy.Concept object

    @property
    def stringValue(self):
        return self.fact.report.asQName(self.value.name) 

    @property
    def asTuple(self):
        return (self.name, self.value.name)

class TypedTaxonomyDefinedDimensionValue(TaxonomyDefinedDimensionValue):

    @property
    def stringValue(self):
        return self.dimension.typedDomainDatatype.stringValue(self.value) if self.value is not None else None

    @property
    def datatype(self):
        return self.dimension.typedDomainDatatype

    def validateDatatype(self):
        if self.datatype.isLegacy:
            raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' has a datatype which is, or is derived from an unsupported legacy datatype" % self.dimension.name)
    
        if isinstance(self.datatype, ListBasedDatatype):
            raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' is derived by list" % self.dimension.name)

        if isinstance(self.datatype, UnionBasedDatatype) and not self.datatype.isDateTimeUnion:
            raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' is derived by union" % self.dimension.name)

        if isinstance(self.datatype, ComplexDatatype):
            raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' is complex" % self.dimension.name)

        if self.datatype.isPrefixedContent:
            raise XBRLError("oime:unsupportedDimensionDataType", "Dimension '%s' has unsupported prefixed content type" % self.dimension.name)

    def validate(self):
        if self.value is None and not self.dimension.nillable:
            raise XBRLError("oime:invalidDimensionValue", "Invalid nil value for non-nillable dimension '%s'" % self.dimension.name)


