from xbrl.xbrlerror import XBRLError
from xbrl.common import RE_NCNAME, RE_QNAME

def isValidIdentifier(i):
    return RE_NCNAME.match(i) is not None and "." not in i

def isValidQName(i):
    return RE_QNAME.match(i) is not None 

def validateURIMap(uriMap):
    r = set()
    for v in uriMap.values():
        if v in r:
            raise XBRLError("oimce:multipleAliasesForURI", "Multiple aliases for URI '%s'" % v)
        r.add(v)


