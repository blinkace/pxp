from lxml import etree
from .schemadocument import SchemaDocument, ElementDefinition, ComplexTypeDefinition, SimpleTypeDefinition
from xbrl.qname import parseQName
from xbrl.const import NS, NSMAP
from xbrl.xml.util import qname


class SchemaParser:

    def parse(self, tree, url):
        schema = SchemaDocument(url)
        root = tree.getroot()
        schema.targetNamespace = root.get('targetNamespace')
        schema.preferredPrefix = next((p for p, ns in root.nsmap.items() if ns == schema.targetNamespace and p is not None), None)
        for e in root:
            if isinstance(e.tag, str):
                tag = etree.QName(e)
                ns = tag.namespace
                name = tag.localname
                if ns == NS.xs:
                    if name == 'element':
                        self.parseElementDefinition(schema, e)
                    elif name == 'complexType':
                        self.parseComplexTypeDefinition(schema, e)
                    elif name == 'simpleType':
                        self.parseSimpleTypeDefinition(schema, e)
                    elif name == 'annotation':
                        self.parseAnnotation(schema, e)
                    elif name == 'import':
                        schema.addXSDImport(e.get("namespace"), e.get("schemaLocation"))
        return schema

    def parseAnnotation(self, schema, annotation):
        for href in annotation.xpath("xs:appinfo/link:linkbaseRef/@xlink:href", namespaces = NSMAP):
            schema.addLinkbaseRef(href)

    def parseElementDefinition(self, schema, e):
        sgqname = e.get("substitutionGroup", None)
        if sgqname:
            sg = parseQName(e.nsmap, sgqname)
        else:
            sg = None

        dtQName = e.get("type", None)
        dte = e
        isComplex = False
        if dtQName is None:
            if len(e.xpath("xs:complexType/xs:complexContent", namespaces = NSMAP)) > 0:
                dtQName = None
                isComplex = True
            else:
                dte = next(iter(e.xpath("xs:complexType/xs:simpleContent/xs:restriction", namespaces = NSMAP)),None)
                if dte is not None:
                    dtQName = dte.get("base", None)

        if dtQName is not None:
            datatype = parseQName(dte.nsmap, dtQName)
        else:
            datatype = None

        periodType = e.get(qname("xbrli:periodType"), None)

        schema.addElement(ElementDefinition(
            e.get("name"), 
            sg, 
            datatype, 
            typedDomainRef = e.get(qname("xbrldt:typedDomainRef"),None),
            elementId = e.get("id", None),
            isComplex = isComplex,
            periodType = periodType,
            isAbstract = e.get("abstract", "false") in {"true", "1"}
            ))

    def parseComplexTypeDefinition(self, schema, e):
        if e.childElement("xs:complexContent") is not None:
            schema.addType(ComplexTypeDefinition(e.get("name"), None, isComplex = True))
        else:
            basetypeElement = next(iter(e.xpath("xs:simpleContent/xs:restriction | xs:simpleContent/xs:extension", namespaces = NSMAP)), None)
            if basetypeElement is not None:
                basetype = basetypeElement.get("base")
            else:
                basetype = None

            if basetype:
                basetype = parseQName(e.nsmap, basetype)

            schema.addType(ComplexTypeDefinition(e.get("name"), basetype))

    def parseSimpleTypeDefinition(self, schema, e):
        basetypeElement = e.childElement(qname("xs:restriction"))
        if basetypeElement is not None:
            basetype = basetypeElement.get("base")
        else:
            basetype = None

        if basetype:
            basetype = parseQName(e.nsmap, basetype)

        schema.addType(SimpleTypeDefinition(e.get("name"), basetype))

            




