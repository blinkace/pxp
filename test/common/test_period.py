from xbrl.common import parsePeriodString
from xbrl import XBRLError
import unittest

class UnitStringTests(unittest.TestCase):

    def test_periodStringRepresentation(self):

        passes = (
            "2020-01-01T10:00:00Z",
            "2020-01-01T10:00:00+10:00",
            "2020-01-01T10:00:00.000+10:00",
            "2020-01-01T10:00:00.000+10",
        )

        for dt in passes:
            parsePeriodString(dt)

        fails = (
            "2020-01-01",
            "2020-01-01T10:00:00+29:00",
            "2020-13-01T10:00:00.000",
            "2020-1-1T10:00:00.000+10",
        )

        for f in fails:
            with self.assertRaises(XBRLError) as e:
                parsePeriodString(f)
