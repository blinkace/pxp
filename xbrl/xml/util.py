from lxml import etree
from xbrl.const import NS

def qname(prefix, local):
    return etree.QName(NS[prefix], local)

def childElements(parent, prefix, local):
    return (e for e in parent if etree.iselement(e) and e.tag == qname(prefix, local))

def childElement(parent, prefix, local):
    return next(childElements(parent, prefix, local), None)


