from lxml import etree
from .schemadocument import SchemaDocument, ElementDefinition, ComplexTypeDefinition, SimpleTypeDefinition, ListSimpleTypeDefinition
from xbrl.qname import parseQName
from xbrl.const import NS, NSMAP
from xbrl.common import SQName
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
            anonDataTypeName = "#anon-%s.type" % e.get("name")
            datatype = SQName(schema.targetNamespace, anonDataTypeName)
            ct = e.childElement(qname("xs:complexType"))
            if ct is not None:
                self.parseComplexTypeDefinition(schema, ct, anonDataTypeName)
            else:
                st = e.childElement(qname("xs:simpleType"))
                if st is not None:
                    self.parseSimpleTypeDefinition(schema, st, anonDataTypeName)
        else:
            datatype = SQName(parseQName(dte.nsmap, dtQName))

        periodType = e.get(qname("xbrli:periodType"), None)

        schema.addElement(ElementDefinition(
            e.get("name"), 
            sg, 
            datatype, 
            typedDomainRef = e.get(qname("xbrldt:typedDomainRef"),None),
            elementId = e.get("id", None),
            periodType = periodType,
            isAbstract = e.get("abstract", "false") in {"true", "1"},
            nillable = e.get("nillable", "false") in {"true", "1"}
            ))

    def parseComplexTypeDefinition(self, schema, e, name = None):
        if name is None:
            name = e.get("name")
        if e.childElement("xs:complexContent") is not None:
            schema.addType(ComplexTypeDefinition(name, None, isComplex = True))
        else:
            basetypeElement = next(iter(e.xpath("xs:simpleContent/xs:restriction | xs:simpleContent/xs:extension", namespaces = NSMAP)), None)
            if basetypeElement is not None:
                basetype = basetypeElement.get("base")
            else:
                basetype = None

            if basetype:
                basetype = SQName(parseQName(e.nsmap, basetype))

            schema.addType(ComplexTypeDefinition(name, basetype))

    # Parse a simple type definition.
    # In the case of an anonymous type definition, a name must be supplied
    def parseSimpleTypeDefinition(self, schema, e, name = None):
        if name is None:
            name = e.get("name")
        basetypeElement = e.childElement(qname("xs:restriction"))
        if basetypeElement is not None:
            basetype = basetypeElement.get("base")
        else:
            basetype = None

        if basetype:
            basetype = SQName(parseQName(e.nsmap, basetype))

        if e.childElement(qname("xs:list")) is not None:
            schema.addType(ListSimpleTypeDefinition(name))
        else:
            schema.addType(SimpleTypeDefinition(name, basetype))


