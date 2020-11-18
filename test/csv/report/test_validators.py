from xbrl.csv.report.validators import isValidIdentifier


def test_validate_identifier():
    assert isValidIdentifier("abcd")
    assert isValidIdentifier("a123bcd")
    assert not isValidIdentifier("1a12bcd")
    assert not isValidIdentifier("a123.bcd")
    assert not isValidIdentifier("|aa12bcd")
    assert not isValidIdentifier("date|greeting")
