from xbrl.const import NS
from xbrl.xml import qname

class Concept:

    def __init__(self, name, typeChain, substitutionGroupChain, typedDomainRef = None):
        self.name = name
        self.typeChain = typeChain
        self.substitutionGroupChain = substitutionGroupChain
        self.typedDomainRef = typedDomainRef

    @property
    def itemType(self):
        return next((dt for dt in self.typeChain if dt.namespace == NS.xbrli), None)

    @property
    def isNumeric(self):
        numericTypes = set(qname("xs", t) for t in ('decimal', 'float', 'double'))
        return not set(self.typeChain).isdisjoint(numericTypes)

    @property
    def isDimension(self):
        return qname("xbrldt:dimensionItem") in self.substitutionGroupChain

    @property
    def isTypedDimension(self):
        return self.typedDomainRef is not None
