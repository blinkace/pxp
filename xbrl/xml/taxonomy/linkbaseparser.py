from lxml import etree
from .linkbase import Linkbase
from xbrl.qname import parseQName
import logging
from .document import Loc
from urllib.parse import urldefrag
from xbrl.xml import qname

class LinkbaseParser:

    def parse(self, tree, url):
        linkbase = Linkbase(url)
        logging.info("Loading linkbase: %s" % url)
        root = tree.getroot()

        for loc in root:
            if loc.tag == qname("link:roleRef"):
                href = urldefrag(loc.get(qname("xlink:href"))).url
                linkbase.addRoleRef(href)
            elif loc.tag == qname("link:arcroleRef"):
                href = urldefrag(loc.get(qname("xlink:href"))).url
                linkbase.addArcroleRef(href)


        for loc in root.iter():
            if loc.tag == qname("link:loc"):
                href = urldefrag(loc.get(qname("xlink:href"))).url
                linkbase.addLoc(href)

        return linkbase

