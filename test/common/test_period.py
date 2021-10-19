from xbrl.common import parsePeriodString
from xbrl import XBRLError
import unittest
from enum import Enum

    

class PeriodTests(unittest.TestCase):



    def test_periodStringRepresentation(self):

        validCanonical = (
            "2020-01-01T10:00:00Z",
            "2020-01-01T10:00:00",
            "2020-01-01T10:00:00.012",
        )

        for dt in validCanonical:
            parsePeriodString(dt)
            parsePeriodString(dt, requireCanonical = True)

        validNonCanonical = (
            "2020-01-01T10:00:00.0",
            "2020-01-01T10:00:00.120",
            "2020-12-01T24:00:00",
            "2020-01-01T10:00:00+10:00",
            "2020-01-01T10:00:00.000+10:00",
            "2020-01-01T10:00:00.000+10",
        )

        for vnc in validNonCanonical:
            with self.assertRaises(XBRLError) as e:
                parsePeriodString(vnc, requireCanonical = True)
            parsePeriodString(vnc, requireCanonical = False)

        fails = (
            "2020-01-01",
            "2020-01-01T10:00:00+29:00",
            "2020-13-01T10:00:00.000",
            "2020-1-1T10:00:00.000+10",
            "2020-12-01T24:00:01",
            "2020-12-01T25:00:01",
        )

        for f in fails:
            with self.assertRaises(XBRLError) as e:
                parsePeriodString(f, requireCanonical = True)
            with self.assertRaises(XBRLError) as e:
                parsePeriodString(f, requireCanonical = False)
