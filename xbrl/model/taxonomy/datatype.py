from xbrl.const import NS
from xbrl.xml import qname, qnameset

class Datatype:

    def __init__(self, datatypeChain):

        self.datatypeChain = datatypeChain

    @property
    def itemType(self):
        return next((dt for dt in self.datatypeChain if dt.namespace == NS.xbrli), None)

    @property
    def isNumeric(self):
        numericTypes = qnameset("xs", {
            'decimal', 
            'float', 
            'double', 
            # derived from decimal:
            # we could manually insert the XS schema into the DTS and then
            # infer all derived types
            'integer', 
            'nonPositiveInteger', 
            'nonNegativeInteger', 
            'positiveInteger', 
            'negativeInteger', 
            'long', 
            'unsignedLong', 
            'int', 
            'unsignedInt', 
            'short', 
            'unsignedShort', 
            'byte', 
            'unsignedByte', 
            })
        return not set(self.datatypeChain).isdisjoint(numericTypes)

    def stringValue(self, v):
        if self.isNumeric:
            return v.strip()
        return v
