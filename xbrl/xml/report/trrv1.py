from .trr import TRRegistry, IXTransform
import re
from xbrl.xbrlerror import XBRLError

class NumCommaDot(IXTransform):

    def transform(self, vin):
        return re.sub(r'[^0-9.]','',vin)

class NumDotComma(IXTransform):

    def transform(self, vin):
        return re.sub(r'[^0-9,]','',vin).replace(',','.')

class DateTransform(IXTransform):

    MONTH_TABLE = list(re.compile(m) for m in 'January|February|March|April|May|June|July|August|September|October|November|December'.split('|'))

    def transform(self, vin):
        vin = " ".join(vin.split())
        m = re.fullmatch(type(self).DATE_RE, vin)
        if m is None:
            raise XBRLError("invalidTransform", "Transform does not match pattern")

        for (i, month_re) in enumerate(DateTransform.MONTH_TABLE):
            if month_re.match(m.groupdict().get('M')):
                month = i + 1
        year = m.groupdict().get('Y')
        if len(year) == 2:
            year = ((int(year) + 50) % 100) + 1950
        else:
            year = int(year)

        return "%04d-%02d-%02d" % (year, month, int(m.groupdict().get('D')))


class DateLongUK(DateTransform):

    DATE_RE = r'(?P<D>\d|\d{2,2}) (?P<M>January|February|March|April|May|June|July|August|September|October|November|December) (?P<Y>\d{2,2}|\d{4,4})'


class TRRv1(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2010-04-20'

    TRANSFORMS = (
        NumCommaDot,
        NumDotComma,
        DateLongUK
    )



