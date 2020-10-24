from xbrl.const import NS
from xbrl.xml import qname

class Concept:

    def __init__(self, name, datatype, substitutionGroupChain):
        self.name = name
        self.datatype = datatype
        self.substitutionGroupChain = substitutionGroupChain

    @property
    def itemType(self):
        return datatype.itemType

    @property
    def isNumeric(self):
        return self.datatype.isNumeric

    @property
    def isDimension(self):
        return qname("xbrldt:dimensionItem") in self.substitutionGroupChain
