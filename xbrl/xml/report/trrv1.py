from .trr import TRRegistry, IXTransform, DateTransform
import re
from xbrl.xbrlerror import XBRLError

class NumCommaDot(IXTransform):

    def transform(self, vin):
        return re.sub(r'[^0-9.]','',vin)

class NumDotComma(IXTransform):

    def transform(self, vin):
        return re.sub(r'[^0-9,]','',vin).replace(',','.')



class DateLongUK(DateTransform):

    DATE_RE = r'(?P<D>\d|\d{2,2}) ((?P<M1>January)|(?P<M2>February)|(?P<M3>March)|(?P<M4>April)|(?P<M5>May)|(?P<M6>June)|(?P<M7>July)|(?P<M8>August)|(?P<M9>September)|(?P<M10>October)|(?P<M11>November)|(?P<M12>December)) (?P<Y>\d{2,2}|\d{4,4})'

class TRRv1(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2010-04-20'

    TRANSFORMS = (
        NumCommaDot,
        NumDotComma,
        DateLongUK
    )



