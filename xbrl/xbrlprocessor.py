from .urlresolver import URLResolver
from .taxonomypackage import TaxonomyPackage
from .xml.report import XBRLReportParser
from .xml.report import IXBRLReportParser
from .common import DocumentClass
from .csv.report import XBRLCSVReportParser
from .json.report import XBRLJSONReportParser
from .conformance.loader import SuiteLoader
from .dts import DTS
import logging
from xbrl.xbrlerror import XBRLError
from xbrl.documentloader import DocumentLoader
import os.path

logger = logging.getLogger(__name__)

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

    def loadXBRLCSVReport(self, report):
        rp = XBRLCSVReportParser(processor = self)
        return rp.parse(report)

    def loadXBRLJSONReport(self, report):
        rp = XBRLJSONReportParser(processor = self)
        return rp.parse(report)

    def loadTestSuite(self, suite):
        cl = SuiteLoader(processor = self)
        return cl.load(suite)

    def addTaxonomyPackage(self, path):
        self.resolver.addPackage(TaxonomyPackage(path))

    def loadTaxonomy(self, entryPoint):
        dts = DTS(entryPoint, self.documentLoader)
        dts.discover()
        return dts.buildTaxonomy()

    def loadReport(self, url, documentClass = None):
        if documentClass is None:
            documentClass = self.identifyDocumentClass(url)
        if documentClass is None:
            return (None, "Unable to identify document type")
        elif documentClass == DocumentClass.INLINE_XBRL:
            logger.info("Loading Inline XBRL file: %s" % url)
            report = self.loadIXBRLReport(url)
        elif documentClass == DocumentClass.XBRL_CSV:
            logger.info("Loading xBRL-CSV file: %s" % url)
            report = self.loadXBRLCSVReport(url)
        elif documentClass == DocumentClass.XBRL_JSON:
            logger.info("Loading xBRL-JSON file: %s" % url)
            report = self.loadXBRLJSONReport(url)
        elif documentClass == DocumentClass.XBRL_2_1:
            logger.info("Loading xBRL-XML file: %s" % url)
            report = self.loadXBRLReport(url)
        else:
            return (None, "Unsupported document class: %s" % documentClass.name)
        return (report, None)



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

    def identifyDocumentClass(self, url):
        return DocumentClass.identify(self.resolver, url)

