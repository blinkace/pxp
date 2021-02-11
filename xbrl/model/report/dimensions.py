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
        super().__init__(etree.QName(NS.xbrl, name))
        self.isCore = True

class ConceptCoreDimension(CoreDimension):

    def __init__(self, concept):
        super().__init__("concept")
        self.concept = concept

    @property
    def asTuple(self):
        return (self.name, self.concept.name)

    @property
    def stringValue(self):
        return self.fact.report.asQName(self.concept.name)


class UnitCoreDimension(CoreDimension):

    def __init__(self, numerators, denominators):
        super().__init__("unit")

        self.numerators = numerators
        self.denominators = denominators

    @property
    def asTuple(self):
        return (self.name, frozenset(self.numerators), frozenset(self.denominators) if self.denominators is not None else frozenset())

    @property
    def stringValue(self):
        numStr = "*".join(sorted(self.fact.report.asQName(n) for n in self.numerators))
        if self.denominators is not None and len(self.denominators) > 0:
            if len(self.numerators) > 1:
                numStr = "(%s)" % numStr
            denomStr = "*".join(sorted(self.fact.report.asQName(n) for n in self.denominators))
            if len(self.denominators) > 1:
                denomStr = "(%s)" % denomStr
            return "%s/%s" % (numStr, denomStr)
        else:
            return numStr

class EntityCoreDimension(CoreDimension):

    def __init__(self, scheme, identifier):
        super().__init__("entity")
        self.scheme = scheme
        self.identifier = identifier

    @property
    def stringValue(self):
        prefix = self.fact.report.getPrefix(self.scheme)
        return "%s:%s" % (prefix, self.identifier)

    @property
    def asTuple(self):
        return (self.name, self.scheme, self.identifier)

class LanguageCoreDimension(CoreDimension):

    def __init__(self, language):
        super().__init__("language")
        self.language = language

    @property
    def stringValue(self):
        return self.language

    @property
    def asTuple(self):
        return (self.name, self.language.lower())
