from .concept import Concept, NoteConcept
from xbrl.const import PREFIX
from xbrl.xbrlerror import XBRLError

class Taxonomy:

    def __init__(self, identifier):
        self.concepts = dict()
        self.ns_to_prefix = PREFIX.copy()
        self.prefix_to_ns = dict()
        self.addConcept(NoteConcept())
        #self.dataTypes = builtInTypes.copy()
        self.identifier = identifier

    def addConcept(self, c):
        self.concepts[c.name] = c

    def addPrefix(self, prefix, ns):
        """
        Adds a prefix => ns binding if there is not already a binding present,
        deconflicting the prefix if required.

        Returns the actual prefix used.
        """
        if ns not in self.ns_to_prefix:
            i = 0
            while True:
                p = "%s%s" % (prefix, str(i) if i > 0 else "")
                if p not in self.ns_to_prefix.values():
                    break
                i += 1
            self.ns_to_prefix[ns] = p
        return self.ns_to_prefix[ns]

    def getPrefix(self, ns, default = None):
        return self.ns_to_prefix.get(ns, default)


    def getDimension(self, name):
        dim = self.concepts.get(name, None)
        if dim is None:
            raise XBRLError("oime:unknownDimension", "Dimension %s is not defined in taxonomy" % (str(name)))
        if not dim.isDimension:
            raise XBRLError("oime:unknownDimension", "%s is not a dimension" % (str(name)))

        return dim




