from .concept import Concept
from xbrl.const import PREFIX

class Taxonomy:

    def __init__(self):
        self.concepts = dict()
        self.ns_to_prefix = PREFIX.copy()
        self.prefix_to_ns = dict()

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
            self.ns_to_prefix[ns] = p
        return self.ns_to_prefix[ns]

    def getPrefix(self, ns, default = None):
        return self.ns_to_prefix.get(ns, default)






