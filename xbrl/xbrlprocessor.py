from .urlresolver import URLResolver
from .taxonomypackage import TaxonomyPackage
from .xml.report import XBRLReportParser
from .xml.report import IXBRLReportParser

class XBRLProcessor:

    def __init__(self):

        self.resolver = URLResolver()
        self.resolver.addPackage(TaxonomyPackage("xbrl-specification-files-20170118.zip"))
        pass


    def loadXBRLReport(self, report):
        rp = XBRLReportParser(processor = self)
        return rp.parse(report)

    def loadIXBRLReport(self, report):
        rp = IXBRLReportParser(processor = self)
        return rp.parse(report)

    def addTaxonomyPackage(self, path):
        self.resolver.addPackage(TaxonomyPackage(path))
