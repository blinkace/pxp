from .trr import TRRegistry, IXTransform, DateTransform
import re

class NumComma(IXTransform):

    INPUT_RE = r'\d+(,\d+)?'

    def _transform(self, vin):
        return re.sub(r',','.',vin)

class NumCommaDot(IXTransform):

    INPUT_RE = r'\d{1,3}(,\d{3,3})*(\.\d+)?'

    def _transform(self, vin):
        return re.sub(r',','',vin)

class NumDash(IXTransform):

    INPUT_RE = r'-'

    def _transform(self, vin):
        return 0

class NumDotComma(IXTransform):

    INPUT_RE = r'\d{1,3}(.\d{3,3})*(,\d+)?'

    def _transform(self, vin):
        return re.sub(r',','.',re.sub(r'\.','',vin))

class NumSpaceDot(IXTransform):

    INPUT_RE = r'\d{1,3}( \d{3,3})*(\.\d+)?'

    def _transform(self, vin):
        return re.sub(r' ','',vin)

class NumSpaceComma(IXTransform):

    INPUT_RE = r'\d{1,3}( \d{3,3})*(,\d+)?'

    def _transform(self, vin):
        return re.sub(',','.',re.sub(r' ','',vin))

class DateSlashUS(DateTransform):

    INPUT_RE = r'(?P<M>\d{1,2})/(?P<D>\d{1,2})/(?P<Y>\d|\d{2,2}|\d{4,4})'

class DateSlashEU(DateTransform):

    INPUT_RE = r'(?P<D>\d{1,2})/(?P<M>\d{1,2})/(?P<Y>\d|\d{2,2}|\d{4,4})'

SHORT_MONTH_RE = '(?:(?P<M1>Jan)|(?P<M2>Feb)|(?P<M3>Mar)|(?P<M4>Apr)|(?P<M5>May)|(?P<M6>Jun)|(?P<M7>Jul)|(?P<M8>Aug)|(?P<M9>Sep)|(?P<M10>Oct)|(?P<M11>Nov)|(?P<M12>Dec))' 
LONG_MONTH_RE = '(?:(?P<M1>January)|(?P<M2>February)|(?P<M3>March)|(?P<M4>April)|(?P<M5>May)|(?P<M6>June)|(?P<M7>July)|(?P<M8>August)|(?P<M9>September)|(?P<M10>October)|(?P<M11>November)|(?P<M12>December))' 

class DateShortUS(DateTransform):

    INPUT_RE = SHORT_MONTH_RE + r' (?P<D>\d|\d{2,2}), (?P<Y>\d{2,2}|\d{4,4})'

class DateLongUS(DateTransform):

    INPUT_RE = LONG_MONTH_RE + r' (?P<D>\d|\d{2,2}), (?P<Y>\d{2,2}|\d{4,4})'

class DateLongUK(DateTransform):

    INPUT_RE = r'(\d|\d{2,2}) ' + LONG_MONTH_RE + r' (\d{2,2}|\d{4,4})'

class DateShortUK(DateTransform):

    INPUT_RE = r'(\d|\d{2,2}) ' + SHORT_MONTH_RE + r' (\d{2,2}|\d{4,4})'

class TRRv1PR(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/2008/inlineXBRL/transformation'

    TRANSFORMS = (
        NumComma,
        NumCommaDot,
        NumDash,
        NumDotComma,
        NumSpaceDot,
        NumSpaceComma,
        DateSlashUS,
        DateSlashEU,
        DateShortUS,
        DateLongUS,
        DateLongUK,
        DateShortUK,
    )



