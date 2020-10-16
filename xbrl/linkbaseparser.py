from lxml import etree
from .linkbase import Linkbase
from .qname import parseQName
from .const import NS
import logging
from .document import Loc
from urllib.parse import urldefrag

class LinkbaseParser:

    def parse(self, tree, url):
        linkbase = Linkbase(url)
        logging.info("Loading linkbase: %s" % url)
        root = tree.getroot()

        for loc in root:
            if loc.tag == etree.QName(NS["link"], "roleRef"):
                href = urldefrag(loc.get(etree.QName(NS["xlink"], "href"))).url
                linkbase.addRoleRef(href)
            elif loc.tag == etree.QName(NS["link"], "arcroleRef"):
                href = urldefrag(loc.get(etree.QName(NS["xlink"], "href"))).url
                linkbase.addArcroleRef(href)


        for loc in root.iter():
            if loc.tag == etree.QName(NS["link"], "loc"):
                href = urldefrag(loc.get(etree.QName(NS["xlink"], "href"))).url
                linkbase.addLoc(href)

        print(linkbase.dtsReferences)
        return linkbase






