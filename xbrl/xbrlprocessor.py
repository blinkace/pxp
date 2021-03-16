from .urlresolver import URLResolver
from .taxonomypackageloader import TaxonomyPackageLoader
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
from xbrl.common import ValidationResult, ValidationMessage, ValidationSeverity
from xbrl.xml import qname
import os.path

logger = logging.getLogger(__name__)

class XBRLProcessor:

    def __init__(self, packageDirs = None):

        self.resolver = URLResolver()
        self.addTaxonomyPackage(os.path.join(os.path.dirname(__file__), "..", "xbrl-specification-files-20170118.zip"))
        self.validationResult = ValidationResult()
        if packageDirs is not None:
            for d in packageDirs:
                self.packages = self.loadPackages(d)
        self.documentLoader = DocumentLoader(url_resolver = self.resolver)


    def loadXBRLReport(self, report: str):
        rp = XBRLReportParser(processor = self)
        return rp.parse(report)

    def loadIXBRLReport(self, url: str, src=None):
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
        tp = TaxonomyPackageLoader().load(path)
        self.resolver.addPackage(tp)

    def loadTaxonomy(self, entryPoint: list):
        dts = DTS(entryPoint, self.documentLoader)
        dts.discover()
        return dts.buildTaxonomy()

    def loadReport(self, url, documentClass = None):
        validationResult = ValidationResult()
        report = None
        if documentClass is None:
            documentClass = self.identifyDocumentClass(url)
        try:
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
                return (None, "Unsupported document class: %s" % documentClass.name, None)
        except XBRLError as e:
            validationResult.add(ValidationMessage(e.code, ValidationSeverity.FATAL, e.message))
        return (report, None, validationResult)

    def loadPackages(self, packageDir):
        if not os.path.isdir(packageDir):
            raise ValueError("%s is not a directory" % packageDir)

        for f in os.listdir(packageDir):
            path = os.path.join(packageDir, f)
            if os.path.isdir(path):
                pass
            elif os.path.isfile(path) and path.lower().endswith(".zip"):
                try:
                    self.addTaxonomyPackage(path)
                except XBRLError as e:
                    logging.warn("Error loading %s: %s" % (path, e.message))

    def identifyDocumentClass(self, url):
        return DocumentClass.identify(self.resolver, url)

