from xbrl.common import parseUnitString
from xbrl import XBRLError
from xbrl.xml import qname
import unittest


class UnitStringTests(unittest.TestCase):

    def test_unitStringRepresentation(self):

        nsmap = {
            "abc": "http://www.example.com/abc",
            "def": "http://www.example.com/abc"
        }

        passes = (
            ("abc:foo", ("abc:foo", ), ()),
            ("abc:foo/abc:def", ("abc:foo", ), ("abc:def", )),
            ("abc:foo/(abc:def*abc:xyz)", ("abc:foo", ), ("abc:def", "abc:xyz")),
        )

        for string, expectedNum, expectedDenom in passes:
            (num, denom) = parseUnitString(string, nsmap)
            self.assertEqual(num, list(qname(e, nsmap) for e in expectedNum))
            self.assertEqual(denom, list(qname(e, nsmap) for e in expectedDenom))


        fails = (
                ("abc foo", "must not contain whitespace"),
                (" abc:foo", "must not contain whitespace"),
                ("xyz:foo", "Undeclared namespace prefix"),
                ("def:zzz*abc:def", "measures must be sorted"),
                ("(abc:zzz*def:def)", "must only be used if a denominator is present"),
                ("(abc:zzz)/def:def", "only be used if more than one measure present"),
                ("abc:zzz/(def:def)", "only be used if more than one measure present"),
                ("abc:aaa*abc:def/def:def", "must be in parentheses"),
                ("(abc:aaa * abc:def)/def:def", "must not contain whitespace"),
                ("(abc:eee*abc:def)/def:def", "must be sorted"),
                ("abc:eee/(def:def*def:aaa)", "must be sorted"),
                )

        for (string, reason) in fails:
            with self.assertRaises(XBRLError) as e:
                parseUnitString(string, nsmap)
            assert reason in str(e.exception)





