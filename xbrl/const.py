import re

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
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    entities = "https://xbrl.org/((~status_date_uri~))/entities"
    entities_cr7 = "https://xbrl.org/2021-02-03/entities"

PREFIX = {}
NSMAP = {}
OIM_COMMON_RESERVED_PREFIXES = {}
OIM_COMMON_RESERVED_PREFIX_MAP = {}


def buildPrefixMaps():
    global PREFIX 
    PREFIX.clear()
    for k, v in NS.__dict__.items():
        if not k.startswith("_"):
            PREFIX[v] = k

    global NSMAP 
    NSMAP.clear()
    for k, v in NS.__dict__.items():
        if not k.startswith("_"):
            NSMAP[k] = v

    global OIM_COMMON_RESERVED_PREFIXES
    OIM_COMMON_RESERVED_PREFIXES = { "iso4217", "utr", "xbrl", "xbrli", "xs" }
    global OIM_COMMON_RESERVED_PREFIX_MAP
    OIM_COMMON_RESERVED_PREFIX_MAP.clear()

    for k in OIM_COMMON_RESERVED_PREFIXES:
        OIM_COMMON_RESERVED_PREFIX_MAP[k] = getattr(NS, k) 

buildPrefixMaps()

def setOIMVersion(version):
    for k, v in NS.__dict__.items():
        if not k.startswith("_"):
            setattr(NS, k, re.sub(r'\(\(~status_date_uri~\)\)', version, v))
    buildPrefixMaps()

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
    xbrlcsv_cr9 = 'https://xbrl.org/CR/2021-07-07/xbrl-csv'
    xbrlcsv_pr1 = 'https://xbrl.org/PR/2021-08-04/xbrl-csv'
    xbrljson_git = 'https://xbrl.org/((~status_date_uri~))/xbrl-json'
    xbrljson_wgwd = 'https://xbrl.org/WGWD/YYYY-MM-DD/xbrl-json'
    xbrljson_cr7 = 'https://xbrl.org/CR/2021-02-02/xbrl-json'
    xbrljson_cr9 = 'https://xbrl.org/CR/2021-07-07/xbrl-json'
    xbrljson_pr1 = 'https://xbrl.org/PR/2021-08-04/xbrl-json'
