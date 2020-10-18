from xbrl.const import NS
from lxml import etree

class Dimension:

    def __init__(self, name):
        self.name = name

class ConceptCoreDimension(Dimension):

    def __init__(self, concept):
        super().__init__(etree.QName(NS['xbrl'], "concept"))
        self.concept = concept


class PeriodCoreDimension(Dimension):
    pass

class EntityCoreDimension(Dimension):

    def __init__(self, scheme, identifier):
        super().__init__(etree.QName(NS['xbrl'], "entity"))
        self.scheme = scheme
        self.identifier = identifier

