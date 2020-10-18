from xbrl.const import NS
from lxml import etree

class Dimension:

    def __init__(self, name):
        self.name = name
        self.isCore = False

    @property
    def stringValue(self):
        return "NOT IMPLEMENTED"


class CoreDimension(Dimension):

    def __init__(self, name):
        super().__init__(etree.QName(NS['xbrl'], name))
        self.isCore = True

class ConceptCoreDimension(CoreDimension):

    def __init__(self, concept):
        super().__init__("concept")
        self.concept = concept


    @property
    def stringValue(self):
        return self.fact.report.asQName(self.concept.name)


class PeriodCoreDimension(CoreDimension):
    pass

class EntityCoreDimension(CoreDimension):

    def __init__(self, scheme, identifier):
        super().__init__("entity")
        self.scheme = scheme
        self.identifier = identifier

    @property
    def stringValue(self):
        prefix = self.fact.report.getPrefix(self.scheme)
        return "%s:%s" % (prefix, self.identifier)
