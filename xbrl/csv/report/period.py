from xbrl.common import parsePeriodString
from xbrl.xbrlerror import XBRLError
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
import re

RE_ISODATE = r'\d{4,}-\d{2}-\d{2}'

def parseAbbreviatedForm(s):

    m = re.match('^' + RE_ISODATE + '$', s) 
    if m is not None:
        start = isoparse(s)
        end = isoparse(s) + timedelta(days=1)
        return (start, end)
    m = re.match(r'^(\d{4,})-(\d{2,})$',s)
    if m is not None:
        start = datetime(int(m.group(1)), int(m.group(2)), 1)
        end = start + relativedelta(months=1)
        return (start, end)
    m = re.match(r'^(\d{4,})$',s)
    if m is not None:
        start = datetime(int(m.group(1)), 1, 1)
        end = start + relativedelta(years=1)
        return (start, end)
    m = re.match(r'^(\d{4,})Q([1-4])$',s)
    # YYYYQn
    if m is not None:
        start = datetime(int(m.group(1)), 1, 1) + relativedelta(months = 3 * (int(m.group(2)) - 1))
        end = start + relativedelta(months=3)
        return (start, end)
    # YYYYHn
    m = re.match(r'^(\d{4,})H([12])$',s)
    if m is not None:
        start = datetime(int(m.group(1)), 1, 1) + relativedelta(months = 6 * (int(m.group(2)) - 1))
        end = start + relativedelta(months=6)
        return (start, end)

    # YYYYWn
    m = re.match(r'^(\d{4,})W(\d{1,2})$',s)
    if m is not None:
        try:
            start = datetime.strptime(s + '-1', '%GW%V-%u')
        except ValueError as e:
            raise XBRLError("xbrlce:invalidPeriodRepresentation", "'%s' is not a valid period string" % s)
        end = start + relativedelta(weeks=1)
        return (start, end)

    raise XBRLError("xbrlce:invalidPeriodRepresentation", "'%s' is not a valid period string" % s)


def parseCSVPeriodString(s):

    try:
        return parsePeriodString(s)
    except XBRLError as e:
        # YYYY-MM-DD..YYYY-MM-DD
        m = re.match('^(' + RE_ISODATE + r')\.\.(' + RE_ISODATE + r')$', s) 
        if m is not None:
            start = isoparse(m.group(1))
            end = isoparse(m.group(2)) + timedelta(days=1)
            return (start, end)

        # Abbreviated forms:
        m = re.match(r'^(.*)@(start|end)$', s) 
        if m is not None:
            (start, end) = parseAbbreviatedForm(m.group(1))
            if m.group(2) == 'start':
                return (start, None)
            else:
                return (end, None)
        else:
            return parseAbbreviatedForm(s)




