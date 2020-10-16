from lxml import etree
from xbrl.const import NS
from xbrl.document import SchemaRef
from xbrl.documentloader import DocumentLoader
from xbrl.xml.util import qname, childElements, childElement

from .context import Context
from urllib.parse import urljoin

class XBRLReportParser:

    def __init__(self, url_resolver):
        self.url_resolver = url_resolver


    def parse(self, url):
        with self.url_resolver.open(url) as src:
            tree = etree.parse(src)
        root = tree.getroot()
        self.contexts = self.parseContexts(root)
        self.taxonomy = self.getTaxonomy(root, url)
        self.parseFacts(root)

#         <xbrli:context id="context_2">
#    <xbrli:entity>
#      <xbrli:identifier scheme="http://www.fca.org.uk/register">898989</xbrli:identifier>
#    </xbrli:entity>
#    <xbrli:period>
#      <xbrli:instant>2016-07-31</xbrli:instant>
#    </xbrli:period>
#  </xbrli:context>


    def parseContexts(self, root):
        contexts = dict()
        for ce in childElements(root, 'xbrli', 'context'):
            c = Context.from_xml(ce)
            contexts[c.id] = c

        return contexts


    def parseFacts(self, root):
        for e in root:
            name = etree.QName(e.tag)
            if name.namespace in (NS['xbrli'], NS['link']):
                continue;
            concept = self.taxonomy.concepts.get(name, None)
            if concept is None:
                raise XBRLError("oime:missingConceptDefinition", "Could not find concept definition for %s" % name.text)
            print("%s (%s) = %s" % (name.text, concept.itemType.text, e.text))
            

    def getTaxonomy(self, root, url):
        schemaRefs = list(SchemaRef(urljoin(url, e.get(etree.QName(NS['xlink'],"href")))) 
            for e in childElements(root, 'link', 'schemaRef'))
        dl = DocumentLoader(url_resolver = self.url_resolver)
        dts = dl.load(schemaRefs)
        return dts.buildTaxonomy()

