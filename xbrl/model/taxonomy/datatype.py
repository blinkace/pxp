from xbrl.const import NS
from xbrl.xml import qname, qnameset
import re

# derived from decimal:
# we could manually insert the XS schema into the DTS and then
# infer all derived types
integerTypes = qnameset("xs", {
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

decimalTypes = qnameset("xs", {
            'decimal' }) | integerTypes

numericTypes = decimalTypes | qnameset("xs", {
            'decimal', 
            'float', 
            'double', 
            })

dateTimeTypes = qnameset("xbrli",{ "dateUnion" }) | qnameset("xs", {
            'date', 
            'dateTime', 
            })

legacyDataTypes = qnameset("xs", {
                    "ENTITY",
                    "ENTITIES",
                    "ID",
                    "IDREF",
                    "IDREFS",
                    "NMTOKEN",
                    "NMTOKENS",
                    "NOTATION"
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

    @property
    def isInteger(self):
        return not set(self.datatypeChain).isdisjoint(integerTypes)

    @property
    def isLegacy(self):
        return not set(self.datatypeChain).isdisjoint(legacyDataTypes)

    def isDtrNamespace(self, qname):
        return qname.namespace.startswith("http://www.xbrl.org/dtr/type/")

    @property
    def isLanguage(self):
        return qname("xs:language") in self.datatypeChain

    def stringValue(self, v):
        if self.isNumeric and v is not None:
            return v.strip()
        return v

    def canonicalValue(self, v):
        if v is None:
            return None
        if self.isDecimal:
            v = v.strip()
            v = re.sub('^(\+|0(?!\.))+','',v)
            v = re.sub('(\..+?)0+$', '\1', v)
            if self.isInteger:
                v = re.sub('\.0$','', v)
        elif self.isNumeric:
            v = v.strip()
        elif self.isLanguage:
            return v.lower().strip()
        return v

    @property
    def datatypeChainTypes(self):
        return self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname).datatypeChain()

class ListBasedDatatype(Datatype):
    pass

class ComplexDatatype(Datatype):
    pass

