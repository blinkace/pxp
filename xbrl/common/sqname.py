from xbrl.xbrlerror import XBRLError
from .regex import RE_NCNAME
import lxml
from xbrl.const import NSMAP

class InvalidSQName(Exception):
    pass

def parseSQName(sqname, nsmap):

    if ":" not in sqname:
        raise InvalidSQName("%s is not a valid SQName" % sqname)

    (prefix, localname) = sqname.split(":", 1)
    if RE_NCNAME.match(prefix) is None:
        raise InvalidSQName("%s is not a valid SQName (invalid prefix)" % sqname)

    uri = nsmap.get(prefix)
    if uri is None:
        raise XBRLError("oimce:unboundPrefix", "Unknown prefix '%s'" % prefix)
    return uri, localname

def sqname(sqname, nsmap = NSMAP):
    (uri, localname) = parseSQName(sqname, nsmap)
    return SQName(uri, localname)

def sqnameset(prefixset, localset, nsmap = NSMAP):
    if type(prefixset) != set:
        prefixset = set([prefixset])
    if type(localset) != set:
        localset = set([localset,])

    return set(SQName(nsmap[p], local) for p in prefixset for local in localset)

class SQName:

    # Call with either a single parameter (an lxml QName) or a
    # namespace/localname pair
    def __init__(self, a, b = None):
        if isinstance(a, lxml.etree.QName):
            self.namespace = a.namespace
            self.localname = a.localname
        else:
            self.namespace = a
            self.localname = b

    def __str__(self):
        return "{%s}%s" % (self.namespace, self.localname)

    def __eq__(self, other):
        if isinstance(other, SQName):
            return self.namespace == other.namespace and self.localname == other.localname
        raise ValueError("Cannot compare SQName to %s" % type(other))

    def __hash__(self):
        return hash((self.namespace, self.localname))

