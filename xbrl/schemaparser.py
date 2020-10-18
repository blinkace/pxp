from lxml import etree
from .schemadocument import SchemaDocument, ElementDefinition, ComplexTypeDefinition
from .qname import parseQName
from .const import NS


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
                if ns == NS["xsd"]:
                    if name == 'element':
                        self.parseElementDefinition(schema, e)
                    elif name == 'complexType':
                        self.parseComplexTypeDefinition(schema, e)
                    elif name == 'annotation':
                        self.parseAnnotation(schema, e)
                    elif name == 'import':
                        schema.addXSDImport(e.get("namespace"), e.get("schemaLocation"))
        return schema

    def parseAnnotation(self, schema, annotation):
        for href in annotation.xpath("xsd:appinfo/link:linkbaseRef/@xlink:href", namespaces = NS):
            schema.addLinkbaseRef(href)

    def parseElementDefinition(self, schema, e):
        sgqname = e.get("substitutionGroup", None)
        if sgqname:
            sg = parseQName(e.nsmap, sgqname)
        else:
            sg = None

        dtQName = e.get("type", None)
        dte = e
        if dtQName is None:
            dte = next(iter(e.xpath("xsd:complexType/xsd:simpleContent/xsd:restriction", namespaces = NS)),None)
            if dte is not None:
                dtQName = dte.get("base", None)

        if dtQName:
            datatype = parseQName(dte.nsmap, dtQName)
        else:
            datatype = None

        schema.addElement(ElementDefinition(e.get("name"), sg, datatype))

    def parseComplexTypeDefinition(self, schema, e):
        basetypeElement = next(iter(e.xpath("xsd:simpleContent/xsd:restriction", namespaces = NS)), None)
        if basetypeElement is not None:
            basetype = basetypeElement.get("base")
        else:
            basetype = None

        if basetype:
            basetype = parseQName(e.nsmap, basetype)

        schema.addType(ComplexTypeDefinition(e.get("name"), basetype))


            




