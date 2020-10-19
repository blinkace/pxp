from lxml import etree
from xbrl.const import NS

def qname(prefix, local = None):
    if ":" in prefix:
        (prefix, local) = prefix.split(":")
    return etree.QName(NS[prefix], local)

