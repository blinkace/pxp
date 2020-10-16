from zipfile import ZipFile
from lxml import etree
from .xml.util import childElements
import os.path
import logging

class TaxonomyPackage:

    def __init__(self, path):
        self.mappings = {}
        self.prefixes = []
        self.path = path

        with self.zipfile() as package:
            self.contents = package.namelist()
            top = {item.split('/')[0] for item in self.contents}
            if len(top) != 1:
                raise ValueError("Multiple top-level directories")

            self.tld = list(top)[0]

            self.loadMetaData(package)

            catalogPath = "%s/META-INF/catalog.xml" % self.tld

            with package.open(catalogPath) as catalogXML:
                catalog = etree.parse(catalogXML)

                for rewrite in childElements(catalog.getroot(), 'catalog', "rewriteURI"):
                    rewriteFrom = rewrite.get("uriStartString")
                    rewriteTo = rewrite.get("rewritePrefix")
                    self.mappings[rewriteFrom] = rewriteTo
            self.prefixes = list(reversed(sorted(self.mappings.keys(), key = lambda x: len(x))))
            logging.info("Loaded '%s'" % self.name)

    def loadMetaData(self, package):
        mdPath = "%s/META-INF/taxonomyPackage.xml" % self.tld
        with package.open(mdPath) as metadataXML:
            metadata = etree.parse(metadataXML)
            root = metadata.getroot()
            names = childElements(root, "tp", "name")
            self.name = next(names).text



    def zipfile(self):
        return ZipFile(self.path)

    def resolve(self, url):
        for prefix in self.prefixes:
            if url.startswith(prefix):
                tail = url[len(prefix):]
                relpath = self.mappings[prefix] + tail
                abspath = os.path.relpath(os.path.join(self.tld, "META-INF", relpath))
                return abspath

        return None

    def hasFile(self, url):
        abspath = self.resolve(url)
        return abspath is not None and abspath in self.contents

    def open(self, url):
        return self.zipfile().open(self.resolve(url))
            


