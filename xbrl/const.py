
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
    oime = "https://xbrl.org/((~status_date_uri~))/oim/error"
    oimce = "https://xbrl.org/((~status_date_uri~))/oim-common/error"
    xbrlxe = "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-xml/error"
    xbrl21e = "http://www.blinkace.com/python-xbrl-oim/xbrl-2.1/error"
    xbrl = "https://xbrl.org/((~status_date_uri~))"
    iso4217 = "http://www.xbrl.org/2003/iso4217"
    utr = "http://www.xbrl.org/2009/utr"
    ix = "http://www.xbrl.org/2013/inlineXBRL"
    ix10 = "http://www.xbrl.org/2008/inlineXBRL"
    ixe = "http://www.xbrl.org/2013/inlineXBRL/error"
    pyxbrle = "https://blinkace.com/pyxbrl/error"
    tpe = 'http://xbrl.org/2016/taxonomy-package/errors'
    xhtml = 'http://www.w3.org/1999/xhtml'
    xbrlce = 'https://xbrl.org/((~status_date_uri~))/xbrl-csv/error'
    xbrlje = 'https://xbrl.org/((~status_date_uri~))/xbrl-json/error'
    enum2 = 'http://xbrl.org/2020/extensible-enumerations-2.0'


PREFIX = {v: k for k, v in NS.__dict__.items() if not k.startswith("_")}
NSMAP = {k: v for k, v in NS.__dict__.items() if not k.startswith("_")}

OIM_COMMON_RESERVED_PREFIXES = { "iso4217", "utr", "xbrl", "xbrli", "xs", "oimce" }
OIM_COMMON_RESERVED_PREFIX_MAP = { k: getattr(NS, k) for k in OIM_COMMON_RESERVED_PREFIXES }

class LinkType:
    footnote = 'http://www.xbrl.org/2003/arcrole/fact-footnote'
    explanatoryFact = 'http://www.xbrl.org/2009/arcrole/fact-explanatoryFact'

class LinkGroup:
    default = 'http://www.xbrl.org/2003/role/link'

LINK_RESERVED_URI_MAP = {
    "_": LinkGroup.default,
    "footnote": LinkType.footnote,
    "explanatoryFact": LinkType.explanatoryFact,
}

class DocumentType:
    xbrlcsv = 'https://xbrl.org/((~status_date_uri~))/xbrl-csv'
    xbrlcsv_cr7 = 'https://xbrl.org/CR/2021-02-03/xbrl-csv'
    xbrljson_git = 'https://xbrl.org/((~status_date_uri~))/xbrl-json'
    xbrljson_wgwd = 'https://xbrl.org/WGWD/YYYY-MM-DD/xbrl-json'
    xbrljson_cr7 = 'https://xbrl.org/CR/2021-02-02/xbrl-csv'
