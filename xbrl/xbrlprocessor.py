from .urlresolver import URLResolver
from .taxonomypackage import TaxonomyPackage
from .xml.report import XBRLReportParser
from .xml.report import IXBRLReportParser
import logging
from xbrl.xbrlerror import XBRLError
import os.path

class XBRLProcessor:

    def __init__(self, packageDirs = None):

        self.resolver = URLResolver()
        self.resolver.addPackage(TaxonomyPackage("xbrl-specification-files-20170118.zip"))
        if packageDirs is not None:
            for d in packageDirs:
                self.packages = self.loadPackages(d)


    def loadXBRLReport(self, report):
        rp = XBRLReportParser(processor = self)
        return rp.parse(report)

    def loadIXBRLReport(self, report):
        rp = IXBRLReportParser(processor = self)
        return rp.parse(report)

    def addTaxonomyPackage(self, path):
        self.resolver.addPackage(TaxonomyPackage(path))


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

