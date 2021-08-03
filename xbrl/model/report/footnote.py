from xbrl.xml import parser
from lxml import etree
from xbrl.xbrlerror import XBRLError

def validateXHTMLContent(v):
    fragment = '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>' % v
    try:
        tree = etree.fromstring(fragment, parser())
    except etree.XMLSyntaxError as e:
        raise XBRLError('oime:invalidXHTMLFragment', "Invalid XHTML found in footnote: %s" % str(e))

    for e in tree.childElements():
        if etree.QName(e.tag).namespace != 'http://www.w3.org/1999/xhtml':
            raise XBRLError('oime:invalidXHTMLFragment', "Element %s is not in XHTML namespace" % e.tag)

    for e in tree.iter():
        if etree.QName(e.tag).namespace == 'http://www.w3.org/1999/xhtml' and e.prefix is not None:
            raise XBRLError('oime:xhtmlElementInNonDefaultNamespace', "Illegal non-default prefix '%s' for XHTML namespace" % e.prefix)



