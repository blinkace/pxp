from .urlresolver import URLResolver
from .taxonomypackage import TaxonomyPackage
from .xml.report import XBRLReportParser

class XBRLProcessor:

    def __init__(self):

        self.resolver = URLResolver()
        self.resolver.addPackage(TaxonomyPackage("xbrl-specification-files-20170118.zip"))
        pass


    def loadXBRLReport(self, report):
        rp = XBRLReportParser(url_resolver = self.resolver)
        rp.parse(report)


    def addTaxonomyPackage(self, path):
        self.resolver.addPackage(TaxonomyPackage(path))
