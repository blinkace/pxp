from xbrl.const import NS
from xbrl.xbrlerror import XBRLError
from .compare import completeDuplicates, consistentDuplicates
import itertools

class Report:

    def __init__(self, taxonomy):
        self.facts = dict()
        self.taxonomy = taxonomy
        self.ns_to_prefix = taxonomy.ns_to_prefix.copy()
        self.usedPrefixes = set()

    def addFact(self, fact):
        self.facts[fact.id] = fact
        fact.report = self

    def getPrefix(self, ns):
        """
        Try to get a prefix from constants, then the taxonomy, then the report,
        creating a new unique prefix if required
        """
        prefix = self.ns_to_prefix.get(ns, None)
        if prefix is None:
            i = 0
            while True:
                prefix = "ns%d" % i
                if prefix not in self.ns_to_prefix:
                    break
                i += 1
            self.ns_to_prefix[ns] = prefix
        self.usedPrefixes.add(prefix)
        return prefix

    def asQName(self, qname):
        return "%s:%s" % (self.getPrefix(qname.namespace), qname.localname)

    def usedPrefixMap(self):
        return { p: n for n, p in self.ns_to_prefix.items() if p in self.usedPrefixes }

    def validate(self):
        for f in self.facts.values():
            f.validate()

    def getDuplicateFacts(self):
        factsByDimensions = dict()
        for f in self.facts.values():
            factsByDimensions.setdefault(f.frozenDimensionSet, set()).add(f)
        duplicates = set()
        for factSet in factsByDimensions.values():
            if len(factSet) > 1:
                duplicates.add(frozenset(factSet))
        return duplicates

    def validateDuplicates(self, permitted):
        duplicates = self.getDuplicateFacts()
        for factSet in duplicates:
            for a, b in itertools.combinations(list(factSet), 2):
                if not permitted(a, b):
                    raise XBRLError("oime:disallowedDuplicateFacts", "Disallowed duplicate facts")

    def validateDuplicatesAllowNone(self):
        self.validateDuplicates(permitted = lambda a, b: False)

    def validateDuplicatesAllowComplete(self):
        self.validateDuplicates(permitted = completeDuplicates)

    def validateDuplicatesAllowConsistent(self):
        self.validateDuplicates(permitted = consistentDuplicates)





