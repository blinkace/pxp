from lxml import etree
from xbrl.const import NSMAP 
from xbrl.xbrlerror import XBRLError

def qname(qstr, nsmap = NSMAP):
    """
    Converts QNames to etree.QName

        qname("xs:foo")

    Prefixes are taken from xbrl.NS

    """
    if ":" in qstr:
        (prefix, local) = qstr.split(":", 1)
    else:
        (prefix, local) = (None, qstr)
    try:
        return etree.QName(nsmap[prefix], local)
    except KeyError:
        raise XBRLError("oimce:unboundPrefix", "Missing namespace prefix (%s)" % prefix)


def qnameset(prefixset, localset, nsmap = NSMAP):
    if type(prefixset) != set:
        prefixset = set([prefixset])
    if type(localset) != set:
        localset = set([localset,])

    return set(etree.QName(nsmap[p], local) for p in prefixset for local in localset)
