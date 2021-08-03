from .document import DTSDocument, XSDImport
from xbrl.const import NS
from xbrl.common import SQName

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
        i = XSDImport(self.resolveURL(url), src = self)
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

    def __init__(self, name: str, substitutionGroup, datatype: SQName, typedDomainRef = None, elementId = None, periodType = None, isAbstract = False, nillable = False) -> None:
        self.id = elementId
        self.name = name
        self.substitutionGroup = substitutionGroup
        self.datatype = datatype
        self.typedDomainRef = typedDomainRef
        self.isAbstract = isAbstract
        self.periodType = periodType
        self.nillable = nillable

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
        if self.datatype is None:
            return []
        if self.datatype.namespace != NS.xs:
            datatypes = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname).datatypeChain()
        else:
            datatypes = []
        return [self.datatype] + datatypes

    # Return the datatype chain as a list of types.  This is messy: it won't
    # include an XML Schema types because we don't have typed definitions for
    # them, so it's useless for determining which schema type something is
    # derived from. 
    #
    # We should really instantiate type objects for the XML Schema types, and
    # then datatypeChain() is a simple transformation to obtain type names from
    # this method.
    def datatypeChainTypes(self):
        # The XML Schema for schemas won't be referenced explicitly, so stop
        # searching for definitions once we get to the XSD namespace - we don't
        # need any further details
        if self.datatype is None:
            return []
        if self.datatype.namespace != NS.xs:
            baseType = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname)
            return [baseType] + baseType.datatypeChainTypes()
        else:
            return []

    @property
    def derivedByList(self):
        return any(isinstance(t, ListSimpleTypeDefinition) for t in self.datatypeChainTypes())

    @property
    def derivedByUnion(self):
        return any(isinstance(t, UnionSimpleTypeDefinition) for t in self.datatypeChainTypes())

    @property
    def isComplexContent(self):
        if self.datatype.namespace != NS.xs:
            baseType = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname)
            return baseType.isComplexContent
        return False

    @property
    def isComplex(self):
        if self.datatype.namespace != NS.xs:
            baseType = self.schemaDocument.getSchemaForNamespace(self.datatype.namespace).getType(self.datatype.localname)
            return isinstance(baseType, ComplexTypeDefinition)
        return False
        

class TypeDefinition:
    def __init__(self, name, base, isComplexContent = False):
        self.name = name
        self.base = base
        self.isComplexContent = isComplexContent

    def datatypeChain(self):
        if self.base is not None:
            if self.base.namespace != NS.xs:
                datatypes = self.schemaDocument.getSchemaForNamespace(self.base.namespace).getType(self.base.localname).datatypeChain()
                return [self.base] + datatypes
            return [self.base]
        else:
            return []

    def datatypeChainTypes(self):
        if self.base is not None:
            if self.base.namespace != NS.xs:
                baseType = self.schemaDocument.getSchemaForNamespace(self.base.namespace).getType(self.base.localname)
                return [baseType] + baseType.datatypeChainTypes()
            return []
        else:
            return []

class ComplexTypeDefinition(TypeDefinition):
    pass

class SimpleTypeDefinition(TypeDefinition):
    pass

class ListSimpleTypeDefinition(SimpleTypeDefinition):

    def __init__(self, name):
        super().__init__(name, None)


class UnionSimpleTypeDefinition(SimpleTypeDefinition):

    def __init__(self, name):
        super().__init__(name, None)
