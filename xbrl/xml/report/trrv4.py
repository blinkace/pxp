from . import trrv2 as trrv2
from .trr import TRRegistry, IXTransform, DateTransform

class FixedFalse(trrv2.BooleanFalse):
    name = 'fixed-false'

class FixedTrue(trrv2.BooleanTrue):
    name = 'fixed-true'

class FixedZero(trrv2.ZeroDash):
    name = 'fixed-zero'

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

class NumDotDecimal(trrv2.NumDotDecimal):
    name = 'num-dot-decimal'

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

        )


