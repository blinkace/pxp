from xbrl.const import NS
from xbrl.xml import qname, qnameset
import re

decimalTypes = qnameset("xs", {
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

numericTypes = decimalTypes | qnameset("xs", {
            'decimal', 
            'float', 
            'double', 
            })

dateTimeTypes = qnameset("xbrli",{ "dateUnion" }) | qnameset("xs", {
            'date', 
            'dateTime', 
            })


class Datatype:

    def __init__(self, datatypeChain):

        self.datatypeChain = datatypeChain

    @property
    def itemType(self):
        return next((dt for dt in self.datatypeChain if dt.namespace == NS.xbrli), None)

    @property
    def isNumeric(self):
        return not set(self.datatypeChain).isdisjoint(numericTypes)

    @property
    def isDateTime(self):
        return not set(self.datatypeChain).isdisjoint(dateTimeTypes)

    @property
    def isText(self):
        for dt in self.datatypeChain:
            if dt in qnameset("xs", { "language", "Name" }):
                return False
            if self.isDtrNamespace(dt) and dt.localname in {"domainItemType", "noLangTokenItemType", "noLangStringItemType"}:
                return False
        return True

    @property
    def isDecimal(self):
        return not set(self.datatypeChain).isdisjoint(decimalTypes)

    def isDtrNamespace(self, qname):
        return qname.namespace.startswith("http://www.xbrl.org/dtr/type/")

    @property
    def isLanguage(self):
        return qname("xs:language") in self.datatypeChain

    def stringValue(self, v):
        if self.isNumeric and v is not None:
            return v.strip()
        return v


