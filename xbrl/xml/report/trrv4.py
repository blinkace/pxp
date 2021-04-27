from . import trrv2 as trrv2
from .trr import TRRegistry, IXTransform, DateTransform

class FixedFalse(trrv2.BooleanFalse):
    name = 'fixed-false'

class FixedTrue(trrv2.BooleanTrue):
    name = 'fixed-true'

class DateDayMonth(trrv2.DateDayMonth):
    name = 'date-day-month'

class NumDotDecimal(trrv2.NumDotDecimal):
    name = 'num-dot-decimal'

class TRRv4(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2020-02-12'

    TRANSFORMS = (
        FixedFalse,
        FixedTrue,
        NumDotDecimal

        )


