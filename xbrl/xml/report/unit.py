from xbrl.xml.util import qname, childElements, childElement

class Unit:

    def __init__(self, uid, numerators, denominators):
        self.id = uid
        self.numerators = numerators
        self.denominators = denominators

    @classmethod
    def from_xml(cls, elt):
        uid = elt.get('id')
        divide = childElement(elt, "xbrli", "divide")
        if divide:
            numerators = list(e.tag for e in childElement("divide", "xbrli", "unitNumerator"))
            denominators = list(e.tag for e in childElement("divide", "xbrli", "unitDenominator"))
        else:
            numerators = list(e.tag for e in elt)
            denominators = None

        return cls(
                uid = uid,
                numerators = numerators,
                denominators = denominators
                )
