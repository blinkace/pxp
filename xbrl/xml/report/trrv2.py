from . import trrv1 as trrv1
from .trr import TRRegistry, IXTransform, DateTransform
import unicodedata
import re

class BooleanTrue(IXTransform):
    INPUT_RE = r'.*'

    def _transform(self, v):
        return "true"

class BooleanFalse(IXTransform):
    INPUT_RE = r'.*'

    def _transform(self, v):
        return "false"

class NoContent(IXTransform):
    INPUT_RE = r'.*'

    def _transform(self, v):
        return ""

class ZeroDash(IXTransform):
    INPUT_RE = r'[\u002d\u058a\u05be\u2010-\u2015\ufe58\ufe63\uff0d]'

    def _transform(self, v):
        return "0"

MONTH_EN_RE = r''' 
                (?:(?P<M1>January|Jan|JAN|JANUARY)|
                (?P<M2>February|Feb|FEB|FEBRUARY)|
                (?P<M3>March|Mar|MAR|MARCH)|
                (?P<M4>Apr|APR|April|APRIL)|
                (?P<M5>May|MAY)|
                (?P<M6>Jun|JUN|June|JUNE)|
                (?P<M7>Jul|JUL|July|JULY)|
                (?P<M8>Aug|AUG|August|AUGUST)|
                (?P<M9>Sep|SEP|September|SEPTEMBER)|
                (?P<M10>Oct|OCT|October|OCTOBER)|
                (?P<M11>Nov|NOV|November|NOVEMBER)|
                (?P<M12>Dec|DEC|December|DECEMBER))
                '''

class DateDayMonthEn(DateTransform):

    INPUT_RE = r'(?x)(?P<D>[0-9]{1,2})[^0-9]+' + MONTH_EN_RE

class DateMonthDayEn(DateTransform):

    INPUT_RE = r'(?x)' + MONTH_EN_RE + '[^0-9]+(?P<D>[0-9]{1,2})[a-zA-Z]{0,2}'

class DateDayMonthYearEn(DateTransform):

    INPUT_RE = r'(?x)(?P<D>[0-9]{1,2})[^0-9]+' + MONTH_EN_RE + '[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateMonthYearEn(DateTransform):

    INPUT_RE = r'(?x)' + MONTH_EN_RE + '[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateYearMonthEn(DateTransform):

    INPUT_RE = r'(?x)(?P<Y>[0-9]{1,2}|[0-9]{4})[^0-9]+' + MONTH_EN_RE

class DateMonthDayYearEn(DateTransform):

    INPUT_RE = r'(?x)' + MONTH_EN_RE + r'[^0-9]+(?P<D>[0-9]{1,2})[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateMonthDayYear(DateTransform):

    INPUT_RE = r'(?P<M>[0-9]{1,2})[^0-9]+(?P<D>[0-9]{1,2})[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateDayMonthYear(DateTransform):

    INPUT_RE = r'(?P<D>[0-9]{1,2})[^0-9]+(?P<M>[0-9]{1,2})[^0-9]+(?P<Y>[0-9]{1,2}|[0-9]{4})'

class DateDayMonth(DateTransform):

    INPUT_RE = r'(?P<D>[0-9]{1,2})[^0-9]+(?P<M>[0-9]{1,2})'

class DateMonthDay(DateTransform):

    INPUT_RE = r'(?P<M>[0-9]{1,2})[^0-9]+(?P<D>[0-9]{1,2})'

class DateYearMonthDayCJK(DateTransform):

    INPUT_RE = r'''(?x)
                (?P<Y>[0-9０-９]{1,2}|[0-9０-９]{4})[\s ]*
                (年)[\s ]*
                (?P<M>[0-9０-９]{1,2})[\s ]*
                (月)[\s ]*
                (?P<D>[0-9０-９]{1,2})[\s ]
                *(日)'''

class DateYearMonthCJK(DateTransform):

    INPUT_RE = r'''(?x)
                (?P<Y>[0-9０-９]{1,2}|[0-9０-９]{4})[\s ]*
                (年)[\s ]*
                (?P<M>[0-9０-９]{1,2})[\s ]*
                (月)
                '''

class DateEraYearMonthDayJP(DateTransform):

    INPUT_RE = r'''(?x)
                (?P<E>明治|明|大正|大|昭和|昭|平成|平|令和|令)[\s ]*
                (?P<Y>[0-9０-９]{1,2}|元)[\s ]*
                (年)[\s ]*
                (?P<M>[0-9０-９]{1,2})[\s ]*
                (月)[\s ]*
                (?P<D>[0-9０-９]{1,2})[\s ]*
                (日)'''

class DateEraYearMonthJP(DateTransform):

    INPUT_RE = r'''(?x)
                (?P<E>明治|明|大正|大|昭和|昭|平成|平|令和|令)[\s ]*
                (?P<Y>[0-9０-９]{1,2}|元)[\s ]*
                (年)[\s ]*
                (?P<M>[0-9０-９]{1,2}) [\s ]*
                (月)'''
                


class NumCommaDecimal(IXTransform):

    INPUT_RE = r'[0-9]{1,3}((\.| | )?[0-9]{3})*(,[0-9]+)?'

    def _transform(self, vin):
        return re.sub(r'[^0-9,]','',vin).replace(',','.')

class NumDotDecimal(IXTransform):

    INPUT_RE = r'[0-9]{1,3}((,| | )?[0-9]{3})*(\.[0-9]+)?'

    def _transform(self, vin):
        return re.sub(r'[^0-9.]','',vin)

class NumUnitDecimal(IXTransform):

    INPUT_RE = r'(?P<I>[0０]|([1-9１-９][0-9０-９]{0,2}((\.|,|，)?[0-9０-９]{3})*))([^0-9,.，．０-９]+)(?P<F>[0-9０-９]{1,2})([^0-9,.，．０-９]*)'

    def _transform(self, vin):
        m = re.fullmatch(NumUnitDecimal.INPUT_RE, unicodedata.normalize('NFKC', vin))
        i = re.sub('[^０-９0-9]','',m.group('I'))
        f = re.sub('[^０-９0-9]','',m.group('F'))
        if f != '':
            return "%s.%02d" % (i, int(f))
        else:
            return i




class TRRv2(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2011-07-31'

    TRANSFORMS = (
        BooleanTrue,
        BooleanFalse,
        DateDayMonthYearEn,
        DateMonthYearEn,
        DateMonthDayYearEn,
        DateDayMonthEn,
        DateMonthDayEn,
        DateYearMonthEn,
        DateMonthDayYear,
        DateDayMonthYear,
        DateDayMonth,
        DateMonthDay,
        DateYearMonthDayCJK,
        DateYearMonthCJK,
        NoContent,
        ZeroDash,
        NumCommaDecimal,
        NumDotDecimal,
        NumUnitDecimal,
        DateEraYearMonthDayJP,
        DateEraYearMonthJP
    )
