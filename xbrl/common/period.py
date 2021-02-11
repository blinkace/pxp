import dateutil.parser
import re
from xbrl.xbrlerror import XBRLError

dateTimeRe = re.compile(r'^(\d{4,}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')
dateRe = re.compile(r'^(\d{4,}-\d{2}-\d{2})((?:(?:\+|-)\d{2}(?:\:\d{2})?|Z)?)$')


def fromISODateTime(s):
    m = dateTimeRe.match(s) 
    if m is None:
        raise ValueError("%s is not a valid ISO8601 date time" % s)

    # XML Schema requires ':' in TZ specifiers, Python requires no colon
    s = m.group(1) + re.sub(':', '', m.group(2))

    return dateutil.parser.isoparse(s)

def fromISODate(s):
    m = dateRe.match(s) 
    if m is None:
        raise ValueError("%s is not a valid ISO8601 date time" % s)

    # XML Schema requires ':' in TZ specifiers, Python requires no colon
    s = m.group(1) + "T00:00:00" +  re.sub(':', '', m.group(2))

    return dateutil.parser.isoparse(s)

def fromISO(s):
    try:
        return fromISODateTime(s)
    except ValueError:
        return fromISODate(s)

def parsePeriodString(s):
    try:
        if '/' in s:
            (start, end) = (fromISODateTime(t) for t in s.split('/',2))
            return (start, end)
        instant = fromISODateTime(s)
        return (instant, None)
    except ValueError as e:
        raise XBRLError("oimce:invalidPeriodRepresentation", "Invalid period string representation: %s" % str(e))


