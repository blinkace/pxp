from xbrl.xbrlerror import XBRLError
from xbrl.common import RE_NCNAME

def isValidIdentifier(i):
    return RE_NCNAME.match(i) is not None and "." not in i

def validateURIMap(uriMap):
    r = set()
    for v in uriMap.values():
        if v in r:
            raise XBRLError("oimce:multipleAliasesForURI", "Multiple aliases for URI '%s'" % v)
        r.add(v)


