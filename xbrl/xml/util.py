from lxml import etree
from xbrl.const import NSMAP

def qname(prefix, local = None):
    """
    Converts QNames to etree.QName

    Usage:

        qname("xs:foo")
        qname("xs", "foo")
        qname({"ns1", "ns2"}, "foo")

    Prefixes are taken from xbrl.NS

    If a set of prefixes is provided.
    """
    if type(prefix) == set:
        return set(qname(p, local) for p in prefix)
    if ":" in prefix:
        (prefix, local) = prefix.split(":")
    return etree.QName(NSMAP[prefix], local)

