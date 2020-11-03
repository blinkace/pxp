import xbrl
from xbrl.const import NS, LinkType, LinkGroup
import os.path
from urllib.request import pathname2url
import datetime


def test_loadixbrl():
    processor = xbrl.XBRLProcessor()
    
    url = "file:" + pathname2url(os.path.abspath(os.path.join(os.path.dirname(__file__), "simple-ixbrl.xhtml")))
    report = processor.loadIXBRLReport(url)
    assert len(report.facts) == 7

    f = report.facts.get("f1")
    assert f is not None
    assert f.value == "This is the first part of a continued tag.This is the second part of a continued tag.This is the third part of a continued tag."
    assert f.stringValue == "This is the first part of a continued tag.This is the second part of a continued tag.This is the third part of a continued tag."
    assert not f.isNumeric
    assert f.unit is None
    assert f.period.isDuration
    assert f.period.stringValue == '2018-01-01T00:00:00/2019-01-01T00:00:00'
    assert f.period.start == datetime.datetime(2018, 1, 1, 0, 0, 0)
    assert f.period.end == datetime.datetime(2019, 1, 1, 0, 0, 0)
    assert f.entity.scheme == 'http://www.example.com/entity'
    assert f.entity.identifier == '12345678'
    footnotes = f.links[LinkType.factFootnote][LinkGroup.default]
    assert len(footnotes) == 2
    fids = set((fn.id for fn in footnotes))
    assert fids == {"fn1", "fn2"}

    f = report.facts.get("f4")
    assert f is not None
    assert f.value == "1234.56"
    assert f.stringValue == "1234.56"
    assert f.isNumeric
    assert f.decimals == 2
    assert f.unit.stringValue == 'iso4217:EUR'
    assert f.period.isDuration
    assert f.period.stringValue == '2018-01-01T00:00:00/2019-01-01T00:00:00'
    assert f.period.start == datetime.datetime(2018, 1, 1, 0, 0, 0)
    assert f.period.end == datetime.datetime(2019, 1, 1, 0, 0, 0)
    assert f.entity.scheme == 'http://www.example.com/entity'
    assert f.entity.identifier == '12345678'

    footnotes = f.links[LinkType.factFootnote][LinkGroup.default]
    assert len(footnotes) == 2
    fids = set((fn.id for fn in footnotes))
    assert fids == {"fn2", "fn4"}

    f = report.facts.get("f5")
    assert f is not None
    assert f.value == "-567000"
    assert f.stringValue == "-567000"
    assert f.isNumeric
    assert f.decimals == 0
    assert f.unit.stringValue == 'iso4217:EUR'
    assert f.period.isDuration
    assert f.period.stringValue == '2017-01-01T00:00:00/2018-01-01T00:00:00'
    assert f.period.start == datetime.datetime(2017, 1, 1, 0, 0, 0)
    assert f.period.end == datetime.datetime(2018, 1, 1, 0, 0, 0)
    assert f.entity.scheme == 'http://www.example.com/entity'
    assert f.entity.identifier == '12345678'

    f = report.facts.get("fn1")
    assert f is not None
    assert f.value == " This is the content of footnote 1. "
    assert f.stringValue == " This is the content of footnote 1. "
    assert not f.isNumeric
    assert f.period is None
    assert f.entity is None

    f = report.facts.get("fn2")
    assert f is not None
    assert f.value == "<p>This is the content of footnote 2.</p>\n    <p>It has <b>bold</b>  and a nested footnote.\n    And a nested fact.\n    \n    </p>\n    "
    assert not f.isNumeric
    assert f.period is None
    assert f.entity is None

    f = report.facts.get("fn4")
    assert f is not None
    assert f.value == "It has <b>bold</b>  and a nested footnote.\n    And a nested fact.\n    "
    assert not f.isNumeric
    assert f.period is None
    assert f.entity is None
