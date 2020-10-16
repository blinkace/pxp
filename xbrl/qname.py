from lxml import etree

def parseQName(nsmap, value):
    if ':' in value:
        pfx, localname = value.split(':', 1)
    else:
        pfx = None
        localname = value

    ns = nsmap.get(pfx)
    if ns is None:
        raise ValueError("Unknown namespace prefix '{0}'!".format(pfx))
    return etree.QName(ns, localname)

