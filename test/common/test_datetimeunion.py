from xbrl.common.period import DateTimeUnion
import unittest

class DateTimeUnionTestsUnitStringTests(unittest.TestCase):


    def test_datetimeunion(self):

        datetimes = (
            "2020-01-01T10:00:00Z",
            "2020-01-01T10:00:00+10:00",
            "2020-01-01T10:00:00.000+10:00",
            "2020-01-01T10:00:00.000+10",
            )

        for dt in datetimes:
            du = DateTimeUnion(dt)
            assert du.isDate is False

        dates = (
            "2020-01-01",
            "2020-01-01Z",
            "2020-01-01+10",
            )

        for d in dates:
            du = DateTimeUnion(d)
            assert du.isDate is True

        assert DateTimeUnion("2020-01-01") != DateTimeUnion("2020-01-01T00:00:00")
        assert DateTimeUnion("2020-01-01") != DateTimeUnion("2020-01-01Z")
        assert DateTimeUnion("2020-01-01+00:00") == DateTimeUnion("2020-01-01Z")
        assert DateTimeUnion("2020-01-01T00:00:00.000") == DateTimeUnion("2020-01-01T00:00:00")
        assert DateTimeUnion("2020-01-01T00:00:00Z") != DateTimeUnion("2020-01-01T00:00:00")





