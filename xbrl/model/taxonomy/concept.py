from lxml import etree
from xbrl.const import NS

class Concept:

    def __init__(self, name, typeChain, substitutionGroupChain):
        self.name = name
        self.typeChain = typeChain
        self.substitutionGroupChain = substitutionGroupChain

    @property
    def itemType(self):
        return next((dt for dt in self.typeChain if dt.namespace == NS['xbrli']), None)

    @property
    def isNumeric(self):
        numericTypes = set(etree.QName(NS['xs'], t) for t in ('decimal', 'float', 'double'))
        print(list(t.text for t in numericTypes))
        print(list(t.text for t in self.typeChain))
        return not set(self.typeChain).isdisjoint(numericTypes)

    @property
    def isDimension(self):
        return etree.QName(NS['xbrldt'], "dimensionItem") in self.substitutionGroupChain

