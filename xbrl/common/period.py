import dateutil.parser
import re
from xbrl.xbrlerror import XBRLError

dateTimeRe = re.compile(r'^(\d{4,}-\d{2}-\d{2}T(\d{2}):\d{2}:\d{2}(?:\.\d+)?)((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')
dateRe = re.compile(r'^(\d{4,}-\d{2}-\d{2})((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')

def fromISODateTime(s):
    m = dateTimeRe.match(s) 
    if m is None:
        raise ValueError("%s is not a valid ISO8601 date time" % s)

    if m.group(2) == '24':
        raise ValueError("Hour component of '24' is not permitted in the canonical form for xs:dateTime (%s)" % s)

    # XML Schema requires ':' in TZ specifiers, Python requires no colon
    s = m.group(1) + re.sub(':', '', m.group(3))

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


def parsePeriodString(s):
    try:
        if '/' in s:
            (start, end) = (fromISODateTime(t) for t in s.split('/',2))
            return (start, end)
        instant = fromISODateTime(s)
        return (instant, None)
    except ValueError as e:
        raise XBRLError("oimce:invalidPeriodRepresentation", "Invalid period string representation: %s" % str(e))


