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

    def __init__(self, raiseFatal = True, qualityCheck = False):
        self.qualityCheck = qualityCheck
        self.raiseFatal = raiseFatal

    def load(self, path):
        self.validationResult = ValidationResult()
        mappings = dict()

        try:

            with ZipFile(path) as package:
                contents = package.namelist()

                for p in contents:
                    if '\\' in p:
                        raise XBRLError("tpe:invalidArchiveFormat", "Archive contains path with '\\'")

                top = {item.split('/')[0] for item in contents}
                if len(top) != 1:
                    raise XBRLError("tpe:invalidDirectoryStructure", "Multiple top-level directories")

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

                        for rewrite in catalog.getroot().childElements(qname("catalog:rewriteURI")):
                            rewriteFrom = rewrite.get("uriStartString")
                            rewriteTo = rewrite.get("rewritePrefix")
                            if rewriteFrom in mappings:
                                raise XBRLError("tpe:multipleRewriteURIsForStartString", "Multiple remappings for '%s'" % rewriteFrom)
                            mappings[rewriteFrom] = rewriteTo
                    prefixes = list(reversed(sorted(mappings.keys(), key = lambda x: len(x))))

                logger.info("Loaded '%s'" % metadata["names"][list(metadata["names"].keys())[0]])

                if self.qualityCheck:
                    self.checkCharacterSetEncoding(package)

            return TaxonomyPackage(path, mappings, prefixes, tld, metadata)
        except XBRLError as e:
            if self.raiseFatal:
                raise e
            validationResult.addException(e)
        return None

    def loadMetaData(self, package, tld):
        mdPath = "%s/META-INF/taxonomyPackage.xml" % tld
        if mdPath not in package.namelist():
            raise XBRLError("tpe:metadataFileNotFound", "%s not found" % mdPath)

        metadata = dict()

        with package.open(mdPath) as metadataXML:
            try:
                metadataXML = etree.parse(metadataXML, parser())
            except etree.XMLSyntaxError as e:
                raise XBRLError("tpe:invalidMetaDataFile", str(e))
            root = metadataXML.getroot()
            metadata["names"] = self.multiLingualElement(list(root.childElements(qname("tp:name"))))

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
                            self.validationResult.addError("tpe:invalidMetadataFile", "Missing href attribute on <entryPointDocument>")
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



