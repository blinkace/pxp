from xbrl.xml import qname

class Unit:

    def __init__(self, uid, numerators, denominators):
        self.id = uid
        self.numerators = numerators
        self.denominators = denominators

    @classmethod
    def from_xml(cls, elt):
        uid = elt.get('id')
        divide = elt.childElement(qname("xbrli:divide"))
        if divide is not None:
            numerators = list(e.tag for e in divide.childElement(qname("xbrli:unitNumerator")))
            denominators = list(e.tag for e in divide.childElement(qname("xbrli:unitDenominator")))
        else:
            numerators = list(e.tag for e in elt)
            denominators = None

        return cls(
                uid = uid,
                numerators = numerators,
                denominators = denominators
                )
