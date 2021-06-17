from zipfile import ZipFile
from lxml import etree
from xbrl.xml import parser, qname
from xbrl.xbrlerror import XBRLError
from xbrl.common import encodeXLinkURI, isValidURIReference, ValidationResult
from urllib.parse import urlparse
import os.path
import logging
import string

from .taxonomypackage import TaxonomyPackage
logger = logging.getLogger(__name__)

class TaxonomyPackageLoader:

    def __init__(self, processor, raiseFatal = True, qualityCheck = False, skipSchemaValidation = False, tolerateInvalidMetadata = False):
        self.qualityCheck = qualityCheck
        self.raiseFatal = raiseFatal
        self.tolerateInvalidMetadata = tolerateInvalidMetadata

        self.metadataSchema = None
        self.catalogSchema = None
        if not skipSchemaValidation:
            p = parser(processor.resolver)
            with processor.resolver.open("http://www.xbrl.org/2016/taxonomy-package.xsd") as f:
                self.metadataSchema = etree.XMLSchema(etree.parse(f, p))
            with processor.resolver.open("http://www.xbrl.org/2016/taxonomy-package-catalog.xsd") as f:
                self.catalogSchema = etree.XMLSchema(etree.parse(f, p))

    def load(self, path):
        self.validationResult = ValidationResult()
        mappings = dict()

        try:

            with ZipFile(path) as package:
                contents = package.namelist()

                for p in contents:
                    if '\\' in p:
                        raise XBRLError("tpe:invalidArchiveFormat", "Archive contains path with '\\'")

                top = {item.split('/')[0] for item in contents if '/' in item}
                if len(top) > 1:
                    raise XBRLError("tpe:invalidDirectoryStructure", "Multiple top-level directories")
                elif len(top) == 0:
                    raise XBRLError("tpe:invalidDirectoryStructure", "No directories found")
                tli = list(item for item in contents if '/' not in item)
                if len(tli) > 0:
                    ee = XBRLError("tpe:invalidDirectoryStructure", 'Files found at top-level: %s' % ", ".join(tli))
                    if not self.tolerateInvalidMetadata:
                        raise(ee)
                    self.validationResult.addException(ee)

                tld = list(top)[0]

                catalogPath = "%s/META-INF/catalog.xml" % tld

                metaInfPath = "%s/META-INF/" % tld
                if not any(p.startswith(metaInfPath) for p in contents):
                    raise XBRLError("tpe:metadataDirectoryNotFound", "Taxonomy package does not contain '%s' directory" % metaInfPath)

                metadata = self.loadMetaData(package, tld)

                if catalogPath in package.namelist():
                    with package.open(catalogPath) as catalogXML:
                        try:
                            catalog = etree.parse(catalogXML, parser())
                        except etree.XMLSyntaxError as e:
                            raise XBRLError("tpe:invalidCatalogFile", str(e))

                        if self.catalogSchema is not None:
                            try:
                                self.catalogSchema.assertValid(catalog)
                            except etree.DocumentInvalid as e:
                                raise XBRLError("tpe:invalidCatalogFile", str(e))

                        for rewrite in catalog.getroot().childElements(qname("catalog:rewriteURI")):
                            rewriteFrom = rewrite.get("uriStartString")
                            rewriteTo = rewrite.get("rewritePrefix")
                            if rewriteFrom in mappings:
                                raise XBRLError("tpe:multipleRewriteURIsForStartString", "Multiple remappings for '%s'" % rewriteFrom)
                            mappings[rewriteFrom] = rewriteTo
                    prefixes = list(reversed(sorted(mappings.keys(), key = lambda x: len(x))))


                if self.qualityCheck:
                    self.checkCharacterSetEncoding(package)

            tp = TaxonomyPackage(path, mappings, prefixes, tld, metadata)
            logger.info("Loaded '%s'" % tp.name)
            return tp
        except XBRLError as e:
            if self.raiseFatal:
                raise e
            self.validationResult.addException(e)
        return None

    def loadMetaData(self, package, tld):
        mdPath = "%s/META-INF/taxonomyPackage.xml" % tld
        if mdPath not in package.namelist():
            raise XBRLError("tpe:metadataFileNotFound", "%s not found" % mdPath)

        metadata = dict()
        invalid = False

        with package.open(mdPath) as metadataXML:
            try:
                metadataXML = etree.parse(metadataXML, parser())
            except etree.XMLSyntaxError as e:
                raise XBRLError("tpe:invalidMetaDataFile", str(e))
            if self.metadataSchema is not None:
                try:
                    self.metadataSchema.assertValid(metadataXML)
                except etree.DocumentInvalid as e:
                    ee = XBRLError("tpe:invalidMetaDataFile", str(e))
                    if not self.tolerateInvalidMetadata:
                        raise ee
                    self.validationResult.addException(ee)
                    invalid = True
            root = metadataXML.getroot()

            # Try to get the package name, even if metadata is invalid
            try:
                metadata["names"] = self.multiLingualElement(list(root.childElements(qname("tp:name"))))
            except XBRLError as e:
                if not self.tolerateInvalidMetadata:
                    raise e
                self.validationResult.addException(e)

            if invalid:
                # Give up now if we failed schema validity
                return metadata

            self.multiLingualElement(list(root.childElements(qname("tp:description"))))
            self.multiLingualElement(list(root.childElements(qname("tp:publisher"))))
            eps = root.childElement(qname("tp:entryPoints"))
            if eps is not None:
                for ep in eps.childElements(qname("tp:entryPoint")):
                    self.multiLingualElement(list(ep.childElements(qname("tp:name"))))
                    self.multiLingualElement(list(ep.childElements(qname("tp:description"))))
                    for epd in ep.childElements(qname("tp:entryPointDocument")):
                        href = epd.get("href", None)
                        if href is None:
                            self.validationResult.addError("tpe:invalidMetaDataFile", "Missing href attribute on <entryPointDocument>")
                            continue;

                        uri = encodeXLinkURI(href)
                        if not isValidURIReference(uri):
                            self.validationResult.addError("tpe:invalidMetadataFile", "%s is not a validate URI" % href)
                            continue;

                        url = urlparse(uri)
                        if self.qualityCheck and url.scheme == 'http':
                            self.validationResult.addQualityIssue("pyxbrle:useOfNonSecureURL", "Entry point '%s' uses the 'http' scheme.  'https' is preferred." % uri)
        return metadata
                        
            
    def multiLingualElement(self, elts):
        strings = dict()
        for e in elts:
            l = e.effectiveLang()
            if l is None:
                raise XBRLError("tpe:missingLanguageAttribute", "Missing language attribute on %s element" % e.tag )
            if l in strings:
                raise XBRLError("tpe:duplicateLanguagesForElement", "Language %s is repeated for element %s" % (l, e.tag) )
            strings[l] = e.text
        return strings

            



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
            
    def checkCharacterSetEncoding(self, package):
        for zi in package.infolist():
            if not(all(c in string.printable for c in zi.filename)) and zi.flag_bits & 0x800 != 0x800:
                self.validationResult.addWarning("pyxbrle:nonUTF8encodedNameInPackage", "The file '%s' contains non-ASCII characters, but is not encoded using UTF-8" % (zi.filename))



