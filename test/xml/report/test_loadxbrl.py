import xbrl
import os.path
from urllib.request import pathname2url
import datetime


def test_loadxbrl():
    processor = xbrl.XBRLProcessor()
    
    url = "file:" + pathname2url(os.path.abspath(os.path.join(os.path.dirname(__file__), "simple.xbrl")))
    report = processor.loadXBRLReport(url)
    assert len(report.facts) == 2

    f = report.facts.get("f1")
    assert f is not None
    assert f.value == " 1234 "
    assert f.stringValue == "1234"
    assert f.isNumeric
    assert f.unit.stringValue == "iso4217:EUR"
    assert f.period.isDuration
    assert f.period.stringValue == '2005-01-01T00:00:00/2006-01-01T00:00:00'
    assert f.period.start == datetime.datetime(2005, 1, 1, 0, 0, 0)
    assert f.period.end == datetime.datetime(2006, 1, 1, 0, 0, 0)
    assert f.entity.scheme == 'http://www.example.com/entity'
    assert f.entity.identifier == '12345678'

    f = report.facts.get("f2")
    assert f is not None
    assert f.value == "4321.37"
    assert f.stringValue == "4321.37"
    assert f.isNumeric
    assert f.unit.stringValue == "iso4217:EUR/xbrli:shares"
    assert not f.period.isDuration
    assert f.period.stringValue == '2005-06-02T00:00:00'
    assert f.period.instant == datetime.datetime(2005, 6, 2, 0, 0, 0)
    assert f.entity.scheme == 'http://www.example.com/entity'
    assert f.entity.identifier == '12345678'

