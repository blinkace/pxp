from .trr import TRRegistry, IXTransform, DateTransform
import re
from . import trrv2 as trrv2

MONTH_DK_RE = r'''(?:
            (?P<M1>jan|Jan|JAN)|
            (?P<M2>feb|Feb|FEB)|
            (?P<M3>mar|Mar|MAR)|
            (?P<M4>apr|Apr|APR)|
            (?P<M5>maj|Maj|MAJ)|
            (?P<M6>jun|Jun|JUN)|
            (?P<M7>jul|Jul|JUL)|
            (?P<M8>aug|Aug|AUG)|
            (?P<M9>sep|Sep|SEP)|
            (?P<M10>okt|Okt|OKT)|
            (?P<M11>nov|Nov|NOV)|
            (?P<M12>dec|DEC|Dec))[^0-9]{0,6}'''

class DateDayMonthDK(DateTransform):

    INPUT_RE = r'''(?x)(?P<D>[0-9]{1,2})[^0-9]+''' + MONTH_DK_RE

class DateDayMonthYearDK(DateTransform):

    INPUT_RE = r'''(?x)(?P<D>[0-9]{1,2})[^0-9]+''' + MONTH_DK_RE + '[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateMonthYearDK(DateTransform):

    INPUT_RE = r'(?x)' + MONTH_DK_RE + '[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateYearMonthDay(DateTransform):

    INPUT_RE = r'(?P<Y>[0-9０-９]{1,2}|[0-9０-９]{4})[^0-9０-９]+(?P<M>[0-9０-９]{1,2})[^0-9０-９]+(?P<D>[0-9０-９]{1,2})'

class DateMonthYear(DateTransform):

    INPUT_RE = r'(?P<M>[0-9]{1,2})[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class NumUnitDecimalIN(trrv2.NumUnitDecimal):

    INPUT_RE = r'''(?x)(?:
                (?P<I>[0-9]{1,3})
                |(?P<I2>([0-9]{1,2}(,|\ |\ ))?([0-9]{2}(,|\ |\ ))*[0-9]{3})([^0-9]+)(?P<F>[0-9]{1,2})([^0-9]*)?
                |(?P<I3>[0-9]+)([^0-9]+)(?P<F2>[0-9]{1,2})([^0-9]*)?)'''

class TRRv3(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2015-02-26'

    TRANSFORMS = trrv2.TRRv2.TRANSFORMS + (
        DateDayMonthDK,
        DateDayMonthYearDK,
        DateMonthYearDK,
        DateYearMonthDay,
        DateMonthYear,
        NumUnitDecimalIN
    )


