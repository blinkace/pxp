
class NS:
    xs = 'http://www.w3.org/2001/XMLSchema'
    link = 'http://www.xbrl.org/2003/linkbase'
    xlink = "http://www.w3.org/1999/xlink"
    xbrli = "http://www.xbrl.org/2003/instance"
    xbrldi = "http://xbrl.org/2006/xbrldi"
    xbrldie = "http://xbrl.org/2005/xbrldi/errors"
    xbrldt = "http://xbrl.org/2005/xbrldt"
    xbrldte = "http://xbrl.org/2005/xbrldt/errors"
    catalog = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
    tp = "http://xbrl.org/2016/taxonomy-package"
    oime = "http://www.xbrl.org/DCR/YYYY-MM-DD/oim/error"
    oimce = "http://www.xbrl.org/((~status_date_uri~))/oim-common/error"
    xbrlxe = "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-xml/error"
    xbrl21e = "http://www.blinkace.com/python-xbrl-oim/xbrl-2.1/error"
    xbrl = "http://www.xbrl.org/WGWD/YYYY-MM-DD"
    iso4217 = "http://www.xbrl.org/2003/iso4217"
    utr = "http://www.xbrl.org/2009/utr"
    ix = "http://www.xbrl.org/2013/inlineXBRL"
    ix10 = "http://www.xbrl.org/2008/inlineXBRL"
    ixe = "http://www.xbrl.org/2013/inlineXBRL/error"
    pyxbrle = "https://blinkace.com/pyxbrl/error"
    tpe = 'http://xbrl.org/2016/taxonomy-package/errors'
    xhtml = 'http://www.w3.org/1999/xhtml'
    xbrlce = 'http://www.xbrl.org/((~status_date_uri~))/oim/csv/error'

PREFIX = {v: k for k, v in NS.__dict__.items() if not k.startswith("_")}
NSMAP = {k: v for k, v in NS.__dict__.items() if not k.startswith("_")}

class LinkType:
    factFootnote = 'http://www.xbrl.org/2003/arcrole/fact-footnote'

class LinkGroup:
    default = 'http://www.xbrl.org/2003/role/link'

class DocumentType:
    xbrlcsv = 'http://www.xbrl.org/((~status_date_uri~))/xbrl-csv'
