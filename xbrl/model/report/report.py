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
        self.factsByDimensions = dict()

    def addFact(self, fact):
        self.facts[fact.id] = fact
        fact.report = self
        self.factsByDimensions.setdefault(fact.frozenDimensionSet, set()).add(fact)

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
                if prefix not in self.ns_to_prefix.values():
                    break
                i += 1
            self.ns_to_prefix[ns] = prefix
        self.usedPrefixes.add(prefix)
        return prefix

    def asQName(self, qname):
        return "%s:%s" % (self.getPrefix(qname.namespace), qname.localname)

    def usedPrefixMap(self):
        return { p: n for n, p in self.ns_to_prefix.items() if p in self.usedPrefixes }

    def inboundLinks(self, fact):
        if not hasattr(self, '_inboundLinkMap'):
            self._inboundLinkMap = dict()
            for src in self.facts.values():
                for linkType, linkGroups in src.links.items():
                    for linkGroup, facts in linkGroups.items():
                        for target in facts:
                            self._inboundLinkMap.setdefault(target, {}).setdefault(linkType, {}).setdefault(linkGroup, set()).add(src)
        return self._inboundLinkMap.get(fact, {})


    def validate(self):
        for f in self.facts.values():
            f.validate()

    def getDuplicateFacts(self):
        duplicates = set()
        for factSet in self.factsByDimensions.values():
            if len(factSet) > 1:
                duplicates.add(frozenset(factSet))
        return duplicates

    def validateDuplicates(self, permitted):
        duplicates = self.getDuplicateFacts()
        for factSet in duplicates:
            for a, b in itertools.combinations(list(factSet), 2):
                if not permitted(a, b):
                    raise XBRLError("oime:disallowedDuplicateFacts", "Disallowed duplicate facts: %s vs %s" % (repr(a), repr(b)))

    def validateDuplicatesAllowNone(self):
        self.validateDuplicates(permitted = lambda a, b: False)

    def validateDuplicatesAllowComplete(self):
        self.validateDuplicates(permitted = completeDuplicates)

    def validateDuplicatesAllowConsistent(self):
        self.validateDuplicates(permitted = consistentDuplicates)

    def compare(self, other, onlyEquivalent = False):
        diffs = []
        if self.taxonomy.identifier != other.taxonomy.identifier:
            diffs.append("Taxonomies differ (%s vs %s)" % (", ".join(i.href for i in self.taxonomy.identifier), ", ".join(i.href for i in self.taxonomy.identifier)))

        for fa in self.facts.values():
            found = False
            for fb in other.facts.values():
                if fa.isEqual(fb, checkId = not onlyEquivalent):
                    found = True
                    break 
            if not found:
                diffs.append("Fact not present in other report: %s" % fa)

        for fa in other.facts.values():
            found = False
            for fb in self.facts.values():
                if fa.isEqual(fb, checkId = not onlyEquivalent):
                    found = True
                    break 
            if not found:
                diffs.append("Fact not present in this report: %s" % fa)


        return diffs





