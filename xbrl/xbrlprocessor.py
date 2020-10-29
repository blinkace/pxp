from .urlresolver import URLResolver
from .taxonomypackage import TaxonomyPackage
from .xml.report import XBRLReportParser
from .xml.report import IXBRLReportParser
from .dts import DTS
import logging
from xbrl.xbrlerror import XBRLError
from xbrl.documentloader import DocumentLoader
import os.path

class XBRLProcessor:

    def __init__(self, packageDirs = None):

        self.resolver = URLResolver()
        self.resolver.addPackage(TaxonomyPackage(os.path.join(os.path.dirname(__file__), "..", "xbrl-specification-files-20170118.zip")))
        if packageDirs is not None:
            for d in packageDirs:
                self.packages = self.loadPackages(d)
        self.documentLoader = DocumentLoader(url_resolver = self.resolver)


    def loadXBRLReport(self, report):
        rp = XBRLReportParser(processor = self)
        return rp.parse(report)

    def loadIXBRLReport(self, url, src=None):
        """
        Load an iXBRL report, optionally taking an open file object from which to pull data
        """
        rp = IXBRLReportParser(processor = self)
        return rp.parse(url, src=src)

    def addTaxonomyPackage(self, path):
        self.resolver.addPackage(TaxonomyPackage(path))

    def loadTaxonomy(self, entryPoint):
        dts = DTS(entryPoint, self.documentLoader)
        dts.discover()
        return dts.buildTaxonomy()

    def loadPackages(self, packageDir):
        if not os.path.isdir(packageDir):
            raise ValueError("%s is not a directory" % packageDir)

        for f in os.listdir(packageDir):
            path = os.path.join(packageDir, f)
            if os.path.isdir(path):
                pass
            elif os.path.isfile(path) and path.lower().endswith(".zip"):
                try:
                    self.resolver.addPackage(TaxonomyPackage(path))
                except XBRLError as e:
                    logging.warn("Error loading %s: %s" % (path, e.message))

