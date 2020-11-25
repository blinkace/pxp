from xbrl.csv.report.period import parseCSVPeriodString
from xbrl.common import parsePeriodString
from xbrl import XBRLError
import unittest

class UnitStringTests(unittest.TestCase):

    def test_csvPeriodStringRepresentation(self):

        passes = (
            ("2020-01-01T10:00:00Z", "2020-01-01T10:00:00Z"),
            ("2020-01-01T10:00:00Z/2021-01-01T10:00:00Z", "2020-01-01T10:00:00Z/2021-01-01T10:00:00Z"),
            ("2020-01-01..2020-12-31", "2020-01-01T00:00:00/2021-01-01T00:00:00"),
            ("2019-06-01", "2019-06-01T00:00:00/2019-06-02T00:00:00"),
            ("2019-06", "2019-06-01T00:00:00/2019-07-01T00:00:00"),
            ("2020", "2020-01-01T00:00:00/2021-01-01T00:00:00"),
            ("2019Q2", "2019-04-01T00:00:00/2019-07-01T00:00:00"),
            ("2019W29", "2019-07-15T00:00:00/2019-07-22T00:00:00"),
            ("2019W29@start", "2019-07-15T00:00:00"),
            ("2019W29@end", "2019-07-22T00:00:00"),
            ("2019Q2@end", "2019-07-01T00:00:00"),
            ("2019-06@start", "2019-06-01T00:00:00"),
            ("2020@end", "2021-01-01T00:00:00"),
        )

        for dt, expected in passes:
            assert parseCSVPeriodString(dt) == parsePeriodString(expected)

        fails = (
            "2020-01-01T00:00:00..2021-01-01T00:00:00",
            "2020-01-01Z..2020-01-01Z",
            "2019W54",
            "2020-01-01..2020-12-31@end", 
            "2020-01-01T10:00:00Z/2021-01-01T10:00:00Z@start",
        )

        for f in fails:
            with self.assertRaises(XBRLError) as e:
                parseCSVPeriodString(f)
