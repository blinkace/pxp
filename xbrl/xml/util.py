from lxml import etree
from xbrl.const import NSMAP 

def qname(qstr, nsmap = NSMAP):
    """
    Converts QNames to etree.QName

        qname("xs:foo")

    Prefixes are taken from xbrl.NS

    """
    if ":" in qstr:
        (prefix, local) = qstr.split(":")
    else:
        (prefix, local) = (None, qstr)
    return etree.QName(nsmap[prefix], local)

def qnameset(prefixset, localset, nsmap = NSMAP):
    if type(prefixset) != set:
        prefixset = set([prefixset])
    if type(localset) != set:
        localset = set([localset,])

    return set(etree.QName(nsmap[p], local) for p in prefixset for local in localset)
