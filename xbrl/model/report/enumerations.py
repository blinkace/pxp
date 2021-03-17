import re
from xbrl.common.validators import isValidQName
from xbrl.xbrlerror import XBRLError
from xbrl.xml.util import qname

class EnumerationValue:

    def __init__(self, value):
        self.value = value

    def fromQNameFormat(value, nsmap = {}, requireCanonical = False):
        if requireCanonical:
            if value.strip() != value:
                raise XBRLError("pyxbrle:nonCanonicalEnumerationValue", "Enumeration value '%s' has leading or trailing whitespace" % value)
        value = value.strip()

        if not isValidQName(value):
            raise XBRLError("pyxbrle:invalidEnumerationValue", "Enumeration value '%s' is not a valid QName" % (value))
        return EnumerationValue(qname(value, nsmap))

    def toURINotation(self):
        s = "{%s}%s" % (self.value.namespace, self.value.localname)


class EnumerationSetValue:

    def __init__(self, values):
        self.values = values

    def fromQNameFormat(value, nsmap = {}, requireCanonical = False):
        if re.search(r'(^ | $|  )', value) is not None:
            raise XBRLError("pyxbrle:invalidEnumerationValue", "Enumeration value '%s' has invalid leading, trailing, or internal space" % value)
        values = value.split(' ')
        if requireCanonical:
            if sorted(values) != values:
                raise XBRLError("pyxbrle:nonCanonicalEnumerationValue", "Canonical enumeration value must be in lexicographical order (%s)" % value)

        enumValues = []
        for v in values:
            if not isValidQName(v):
                raise XBRLError("pyxbrle:invalidEnumerationValue", "Enumeration value '%s' (from set value '%s') is not a valid QName" % (v, value))
            enumValues.append(qname(v, nsmap))
        return EnumerationSetValue(enumValues)

    def toURINotation(self):
        s = " ".join("{%s}%s" % (v.namespace, v.localname) for v in self.values)





