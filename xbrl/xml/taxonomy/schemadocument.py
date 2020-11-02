from .document import DTSDocument, XSDImport
from xbrl.const import NS

class SchemaDocument(DTSDocument):

    def __init__(self, url):
        super().__init__(url)
        self.targetNamespace = None
        self.elements = dict()
        self.elementsById = dict()
        self.types = dict()
        self.imports = dict()


    def addElement(self, elt):
        self.elements[elt.name] = elt
        if elt.id:
            self.elementsById[elt.id] = elt
        elt.schemaDocument = self

    def addType(self, datatype):
        self.types[datatype.name] = datatype
        datatype.schemaDocument = self

    def addXSDImport(self, ns, url):
        i = XSDImport(self.resolveURL(url))
        self.dtsReferences.add(i)
        self.imports[ns] = i

    def getSchemaForNamespace(self, ns):
        if ns == self.targetNamespace:
            return self
        i = self.imports.get(ns)
        if i is None:
            raise ValueError("Failed to find import for %s" % ns)
        return self.documentCache.getDocument(i.href)

    def getElement(self, name):
        return self.elements[name]

    def getElementById(self, id):
        return self.elementsById[id]

    def getType(self, datatype):
        return self.types[datatype]


class ElementDefinition:
    def __init__(self, name, substitutionGroup, datatype, typedDomainRef = None, elementId = None):
        self.id = elementId
        self.name = name
        self.substitutionGroup = substitutionGroup
        self.datatype = datatype
        self.typedDomainRef = typedDomainRef

    def substitutionGroups(self):
        sgs = []
        sg = self.substitutionGroup
        if sg is not None:
            sgs = self.schemaDocument.getSchemaForNamespace(sg.namespace).getElement(sg.localname).substitutionGroups()
            sgs.append(sg)
        return sgs

    def datatypeChain(self):
        # The XML Schema for schemas won't be referenced explicitly, so stop
        # searching for definitions once we get to the XSD namespace - we don't
        # need any further details
        if self.datatype.namespace != NS.xs:
            datatypes = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname).datatypeChain()
        else:
            datatypes = []
        return [self.datatype] + datatypes
        

class TypeDefinition:
    def __init__(self, name, base):
        self.name = name
        self.base = base

    def datatypeChain(self):
        if self.base is not None:
            if self.base.namespace != NS.xs:
                datatypes = self.schemaDocument.getSchemaForNamespace(self.base.namespace).getType(self.base.localname).datatypeChain()
                return [self.base] + datatypes
            return [self.base]

        else:
            return []

class ComplexTypeDefinition(TypeDefinition):
    pass

class SimpleTypeDefinition(TypeDefinition):
    pass


