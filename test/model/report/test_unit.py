from xbrl.model.report import Report, Fact, UnitCoreDimension
from xbrl.model.taxonomy import Taxonomy
from xbrl.xml import qname


def test_unit_string_representation():

    tests = [
        {
            "in": [ [ qname("iso4217:USD") ], None ],
            "out": "iso4217:USD"
        },
        {
            "in": [ [ qname("iso4217:USD") ], [ qname("xbrli:shares") ] ],
            "out": "(iso4217:USD)/(xbrli:shares)"
        },
        {
            "in": [ [ qname("iso4217:USD"), qname("xbrli:shares") ], [ qname("utr:madeup")] ],
            "out": "(iso4217:USD*xbrli:shares)/(utr:madeup)"
        },
        {
            "in": [ [ qname("iso4217:USD"), qname("iso4217:GBP"), qname("iso4217:EUR") ], [ qname("utr:madeup") ] ],
            "out": "(iso4217:EUR*iso4217:GBP*iso4217:USD)/(utr:madeup)"
        }

    ]

    for t in tests:
        r = Report(Taxonomy([]))
        unit = UnitCoreDimension(t["in"][0], t["in"][1])
        f = Fact("f1", dimensions = {unit})
        r.addFact(f)
    assert unit.stringValue == t["out"]

    
