import dateutil.parser
import re
from xbrl.xbrlerror import XBRLError

dateTimeRe = re.compile(r'^(\d{4,}-\d{2}-\d{2}T(\d{2}):\d{2}:\d{2}(\.\d+)?)((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')
dateRe = re.compile(r'^(\d{4,}-\d{2}-\d{2})((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')

def validateCanonicalDateTime(s):
    m = dateTimeRe.match(s) 
    if m is None:
        return "%s is not a valid ISO 8601 date time" % s

    if m.group(2) == '24':
        return "Hour component of '24' is not permitted in canonical date time value ('%s')" % s

    if m.group(3) is not None and m.group(3).endswith('0'):
        return "Fractional seconds must not have trailing zeros in canonical date time value ('%s')" % s

    if m.group(4) != '' and m.group(4) != 'Z':
        return "Canonical date times with a time zone must use a time zone of 'Z' ('%s')" % s

    return None

def isCanonicalDateTime(s):
    return validateCanonicalDateTime(s) is None

def fromISODateTime(s, requireCanonical = False):
    m = dateTimeRe.match(s) 
    if m is None:
        raise ValueError("%s is not a valid ISO8601 date time" % s)

    if requireCanonical:
        msg = validateCanonicalDateTime(s)
        if msg is not None:
            raise ValueError(msg)

    # XML Schema requires ':' in TZ specifiers, Python requires no colon
    s = m.group(1) + re.sub(':', '', m.group(4))

    return dateutil.parser.isoparse(s)

def fromISODate(s):
    m = dateRe.match(s) 
    if m is None:
        raise ValueError("%s is not a valid ISO8601 date time" % s)

    # XML Schema requires ':' in TZ specifiers, Python requires no colon
    s = m.group(1) + "T00:00:00" +  re.sub(':', '', m.group(2))

    return dateutil.parser.isoparse(s)


class DateTimeUnion:

    def __init__(self, datetimeUnionStr):
        try:
            self.datetime = fromISODateTime(datetimeUnionStr)
            self.isDate = False
        except ValueError:
            self.datetime = fromISODate(datetimeUnionStr)
            self.isDate = True

    def __eq__(self, other):
        return isinstance(other, DateTimeUnion) and other.isDate == self.isDate and other.datetime == self.datetime

    def __str__(self):
        if self.isDate:
            return re.sub(r'T[\d.:]+', self.datetime.isoformat(), '')
        else:
            return self.datetime.isoformat()


def parsePeriodString(s, requireCanonical = False):
    try:
        if '/' in s:
            (start, end) = (fromISODateTime(t, requireCanonical = requireCanonical) for t in s.split('/',2))
            return (start, end)
        instant = fromISODateTime(s, requireCanonical = requireCanonical)
        return (instant, None)
    except ValueError as e:
        raise XBRLError("oimce:invalidPeriodRepresentation", "Invalid period string representation: %s" % str(e))


