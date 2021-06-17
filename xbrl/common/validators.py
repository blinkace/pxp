from xbrl.common import RE_NCNAME, RE_QNAME
from xbrl.xbrlerror import XBRLError
import re
from .uri_validate import isValidAbsoluteURI, encodeXLinkURI, isValidURIReference

def isValidQName(i):
    return RE_QNAME.match(i) is not None 

def isValidNCName(i):
    return RE_NCNAME.match(i) is not None 

def validateURIMap(uriMap, reservedPrefixMap = {}):
    reservedURIMap = { reservedPrefixMap.get(k): k for k in reservedPrefixMap }
    r = set()
    for prefix, v in uriMap.items():
        # Normalise whitespace
        if " ".join(v.split()) != v:
            # Not a real error code - needs to be re-cast
            raise XBRLError("oimce:invalidStructure", "'%s' is not in canonical form" % v)

        uriRef = encodeXLinkURI(v)

        if not isValidURIReference(uriRef):
            # Not a real error code - needs to be re-cast
            raise XBRLError("oimce:invalidStructure", "'%s' is not a valid URI Reference" % v)

        # URIs technically don't have a fragment, so remove before checking if it's absolute
        uri = re.sub(r'#.*', '', uriRef)
        if not isValidAbsoluteURI(uri):
            raise XBRLError("oimce:invalidURI", "'%s' is not a valid Absolute URI" % v)

        # Duplicate checks apply to the raw value, not the URI
        if v in r:
            raise XBRLError("oimce:multipleAliasesForURI", "Multiple aliases for URI '%s'" % v)
        r.add(v)

        if prefix in reservedPrefixMap and uri != reservedPrefixMap.get(prefix):
            raise XBRLError("oimce:invalidURIForReservedAlias", "Invalid URI '%s' for reserved prefix '%s'" % (v, prefix))

        if v in reservedURIMap and prefix != reservedURIMap.get(v):
            raise XBRLError("oimce:invalidAliasForReservedURI", "Invalid prefix '%s' for reserved URI '%s'" % (prefix, v))


# Checks if the string is a valid xs:anyURI, which we take to be something
# that transforms into a valid URIReference after applying XLink encoding
# of disallowed characters.
def isValidAnyURI(uri):
    return isValidURIReference(encodeXLinkURI(uri.strip()))

def isCanonicalAnyURI(uri):
    return " ".join(uri.split()) == uri


