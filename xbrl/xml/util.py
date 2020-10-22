from lxml import etree
from xbrl.const import NSMAP

def qname(prefix, local = None):
    if ":" in prefix:
        (prefix, local) = prefix.split(":")
    return etree.QName(NSMAP[prefix], local)

