import io
import urllib.request
import urllib.error
import logging

from .xbrlerror import XBRLError

logger = logging.getLogger(__name__)

class URLResolver:

    def __init__(self):
        self.packages = []

    def addPackage(self, package):
        self.packages.append(package)

    def open(self, url):
        for p in self.packages:
            if p.hasFile(url):
                logger.debug("Opening %s from package" % url)
                return p.open(url)
        try:
            logger.debug("Opening %s" % url)
            return urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            raise XBRLError("pyxbrle:HTTPError", "Unable to open %s: %s %s" % (url, e.code, e.reason))



    

