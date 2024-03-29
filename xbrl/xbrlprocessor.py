from .urlresolver import URLResolver
from .taxonomypackageloader import TaxonomyPackageLoader
from .xml.report import XBRLReportParser
from .xml.report import IXBRLReportParser
from .csv.report import XBRLCSVReportParser
from .json.report import XBRLJSONReportParser
from .conformance.loader import SuiteLoader
from .dts import DTS
import logging
from xbrl.xbrlerror import XBRLError
from xbrl.documentloader import DocumentLoader
from xbrl.common import ValidationResult, ValidationMessage, ValidationSeverity, DocumentClass, UnknownDocumentClassError, MissingDocumentClassError
from xbrl.xml import qname
from urllib.parse import urlparse, unquote
from .reportpackageloader import ReportPackageLoader
import os.path

logger = logging.getLogger(__name__)

class XBRLProcessor:

    def __init__(self, packageDirs = None, packagesOnly = False):

        self.resolver = URLResolver(packagesOnly = packagesOnly)

        # Bootstrap taxonomy packages: load these with skipSchemaValidation
        # because they're needed to do schema validation
        tpl = TaxonomyPackageLoader(self, skipSchemaValidation = True)
        self.resolver.addPackage(tpl.load(os.path.join(os.path.dirname(__file__), "packages","xbrl-specification-files-20170118.zip")))
        self.resolver.addPackage(tpl.load(os.path.join(os.path.dirname(__file__), "packages","xml-2001-03.zip")))

        self.addTaxonomyPackage(os.path.join(os.path.dirname(__file__), "packages","dtr-2020-01-21.zip"))
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
        tpl = TaxonomyPackageLoader(self, tolerateInvalidMetadata = True)
        tp = tpl.load(path)
        self.resolver.addPackage(tp)
        return tpl.validationResult

    def loadTaxonomy(self, entryPoint: list):
        dts = DTS(entryPoint, self.documentLoader)
        dts.discover()
        return dts.buildTaxonomy()

    def loadReport(self, url, documentClass = None):
        validationResult = ValidationResult()
        report = None
        try:
            if documentClass is None:
                documentClass = self.identifyDocumentClass(url)
            if documentClass is None:
                return (None, "Unable to identify document type", None)
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
            elif documentClass == DocumentClass.REPORT_PACKAGE:
                logger.info("Loading Report Package: %s" % url)
                return self.loadReportPackage(url)
            else:
                return (None, "Unsupported document class: %s" % documentClass.name, None)
        except XBRLError as e:
            validationResult.add(ValidationMessage(e.code, ValidationSeverity.FATAL, e.message))
        except UnknownDocumentClassError as e:
            validationResult.addFatalError("oimce:unsupportedDocumentType", str(e))
        except MissingDocumentClassError as e:
            validationResult.addFatalError("oimce:unsupportedDocumentType", str(e))
        return (report, None, validationResult)

    def loadReportPackage(self, reportPackageURL: str):
        purl = urlparse(reportPackageURL)
        if purl.scheme != 'file':
            raise XBRLError("pyxbrle:unsupportedURLScheme", "Report Packages can only be loaded from file URLs")

        vr = self.addTaxonomyPackage(unquote(purl.path))
        rp = ReportPackageLoader().load(unquote(purl.path))
        urls = rp.reportURLs()
        if len(urls) != 1:
            raise XBRLError("pyxbrle:reportNotFound", "Report Package does not contain exactly one report")

        (report, err, report_vr) = self.loadReport(urls[0])
        vr.merge(report_vr) 
        return (report, err, vr)

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

