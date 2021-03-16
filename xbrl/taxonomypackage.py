from zipfile import ZipFile
from lxml import etree
from xbrl.xml import parser, qname
from xbrl.xbrlerror import XBRLError
from xbrl.common import encodeXLinkURI, isValidURIReference
from urllib.parse import urlparse
import os.path
import logging
import string

logger = logging.getLogger(__name__)

class TaxonomyPackage:

    def __init__(self, path, mappings, prefixes, tld, metadata):
        self.mappings = mappings
        self.prefixes = prefixes
        self.tld = tld
        self.path = path
        self.metadata = metadata

        with self.zipfile() as package:
            self.contents = package.namelist()

    def zipfile(self):
        return ZipFile(self.path)

    def resolve(self, url):
        for prefix in self.prefixes:
            if url.startswith(prefix):
                logger.debug("Remapping - prefix match for %s in %s" % (url, self.name))
                tail = url[len(prefix):]
                relpath = self.mappings[prefix] + tail
                abspath = os.path.relpath(os.path.join(self.tld, "META-INF", relpath))
                logger.debug(abspath)
                return abspath

        return None

    def hasFile(self, url):
        abspath = self.resolve(url)
        return abspath is not None and abspath in self.contents

    def open(self, url):
        return self.zipfile().open(self.resolve(url))

    @property
    def name(self):
        # XXX replace with a MultiLingualElement object and a sensible way to get a default
        self.metadata["names"][list(self.metadata["names"].keys())[0]]

            
