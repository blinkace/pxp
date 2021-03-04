from zipfile import ZipFile
from lxml import etree
from xbrl.xml import parser, qname
from xbrl.xbrlerror import XBRLError
import os.path
import logging

class TaxonomyPackage:

    def __init__(self, path):
        self.mappings = {}
        self.prefixes = []
        self.path = path

        with self.zipfile() as package:
            self.contents = package.namelist()

            for path in self.contents:
                if '\\' in path:
                    raise XBRLError("tpe:invalidArchiveFormat", "Archive contains path with '\\'")

            top = {item.split('/')[0] for item in self.contents}
            if len(top) != 1:
                raise XBRLError("tpe:invalidDirectoryStructure", "Multiple top-level directories")

            self.tld = list(top)[0]


            catalogPath = "%s/META-INF/catalog.xml" % self.tld

            metaInfPath = "%s/META-INF/" % self.tld
            if not any(p.startswith(metaInfPath) for p in self.contents):
                raise XBRLError("tpe:metadataDirectoryNotFound", "Taxonomy package does not contain '%s' directory" % metaInfPath)

            self.loadMetaData(package)

            if catalogPath in package.namelist():
                with package.open(catalogPath) as catalogXML:
                    try:
                        catalog = etree.parse(catalogXML, parser())
                    except etree.XMLSyntaxError as e:
                        raise XBRLError("tpe:invalidCatalogFile", str(e))


                    for rewrite in catalog.getroot().childElements(qname("catalog:rewriteURI")):
                        rewriteFrom = rewrite.get("uriStartString")
                        rewriteTo = rewrite.get("rewritePrefix")
                        self.mappings[rewriteFrom] = rewriteTo
                self.prefixes = list(reversed(sorted(self.mappings.keys(), key = lambda x: len(x))))
            logging.info("Loaded '%s'" % self.name)

    def loadMetaData(self, package):
        mdPath = "%s/META-INF/taxonomyPackage.xml" % self.tld
        if mdPath not in package.namelist():
            raise XBRLError("tpe:metadataFileNotFound", "%s not found" % mdPath)

        with package.open(mdPath) as metadataXML:
            try:
                metadata = etree.parse(metadataXML, parser())
            except etree.XMLSyntaxError as e:
                raise XBRLError("tpe:invalidMetaDataFile", str(e))
            root = metadata.getroot()
            names = root.childElements(qname("tp:name"))
            self.name = next(names).text



    def zipfile(self):
        return ZipFile(self.path)

    def resolve(self, url):
        for prefix in self.prefixes:
            if url.startswith(prefix):
                logging.debug("Remapping - prefix match for %s in %s" % (url, self.name))
                tail = url[len(prefix):]
                relpath = self.mappings[prefix] + tail
                abspath = os.path.relpath(os.path.join(self.tld, "META-INF", relpath))
                logging.debug(abspath)
                return abspath

        return None

    def hasFile(self, url):
        abspath = self.resolve(url)
        return abspath is not None and abspath in self.contents

    def open(self, url):
        return self.zipfile().open(self.resolve(url))
            


