from . import trrv2 as trrv2
from .trr import TRRegistry, IXTransform, DateTransform
import re

class FixedFalse(trrv2.BooleanFalse):
    name = 'fixed-false'

class FixedTrue(trrv2.BooleanTrue):
    name = 'fixed-true'

class FixedZero(IXTransform):
    name = 'fixed-zero'
    INPUT_RE = r'.*'

    def _transform(self, v):
        return "0"

class FixedEmpty(trrv2.NoContent):
    name = 'fixed-empty'

class DateDayMonth(trrv2.DateDayMonth):
    name = 'date-day-month'

class DateDayMonthEn(trrv2.DateDayMonthEn):
    name = 'date-day-monthname-en'

class DateDayMonthYearEn(trrv2.DateDayMonthYearEn):
    name = 'date-day-monthname-year-en'

class DateMonthDay(trrv2.DateMonthDay):
    name = 'date-month-day'

class DateMonthDayNameEn(trrv2.DateMonthDayEn):
    name = 'date-monthname-day-en'

class NumDotDecimal(IXTransform):
    name = 'num-dot-decimal'
    INPUT_RE = r'[,  0-9]*(\.[ 0-9]+)?'

    def _transform(self, vin):
        return re.sub(r'[^0-9.]','',vin)

class NumCommaDecimal(IXTransform):
    name = 'num-comma-decimal'
    INPUT_RE = r'[\.  0-9]*(,[  0-9]+)?'

    def _transform(self, vin):
        return re.sub(r'[^0-9,]','',vin).replace(',','.')

class TRRv4(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2020-02-12'

    TRANSFORMS = (
        FixedFalse,
        FixedTrue,
        FixedZero,
        FixedEmpty,
        DateDayMonth,
        DateDayMonthEn,
        DateDayMonthYearEn,
        DateMonthDay,
        DateMonthDayNameEn,
        NumDotDecimal,
        NumCommaDecimal,

        )


