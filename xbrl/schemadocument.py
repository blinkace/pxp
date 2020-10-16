from .document import DTSDocument, XSDImport

class SchemaDocument(DTSDocument):

    def __init__(self, url):
        super().__init__(url)
        self.targetNamespace = None
        self.elements = dict()
        self.types = dict()
        self.imports = dict()


    def addElement(self, elt):
        self.elements[elt.name] = elt
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
        return self.dts.getDocument(i.href)

    def getElement(self, name):
        return self.elements[name]

    def getType(self, datatype):
        return self.types[datatype]


class ElementDefinition:
    def __init__(self, name, substitutionGroup, datatype):
        self.name = name
        self.substitutionGroup = substitutionGroup
        self.datatype = datatype

    def substitutionGroups(self):
        sgs = []
        sg = self.substitutionGroup
        if sg is not None:
            sgs = self.schemaDocument.getSchemaForNamespace(sg.namespace).getElement(sg.localname).substitutionGroups()
            sgs.append(sg)
        return sgs

    def datatypeChain(self):
        datatypes = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname).datatypeChain()
        return [self.datatype] + datatypes
        

class ComplexTypeDefinition:
    def __init__(self, name, base):
        self.name = name
        self.base = base

    def datatypeChain(self):
        if self.base is not None:
            datatypes = self.schemaDocument.getSchemaForNamespace(self.base.namespace).getType(self.base.localname).datatypeChain()
            return [self.base] + datatypes

        else:
            return []

