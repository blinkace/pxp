from . import trrv2 as trrv2
from .trr import TRRegistry, IXTransform, DateTransform, number_format
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

    # If decimal separator is present, must be at least one digit after
    # separator, otherwise must be at least one non-fractional digit.
    def validate(self, vin):
        if re.search(r'[0-9]', vin) is None:
            return False
        return super().validate(vin)

    def _transform(self, vin):
        return number_format(re.sub(r'[^0-9.]','',vin))

class NumCommaDecimal(IXTransform):
    name = 'num-comma-decimal'
    INPUT_RE = r'[\.  0-9]*(,[  0-9]+)?'

    # If decimal separator is present, must be at least one digit after
    # separator, otherwise must be at least one non-fractional digit.
    def validate(self, vin):
        if re.search(r'[0-9]', vin) is None:
            return False
        return super().validate(vin)

    def _transform(self, vin):
        return number_format(re.sub(r'[^0-9,]','',vin).replace(',','.'))

class NumUnitDecimal(IXTransform):
    name = 'num-unit-decimal'
    INPUT_RE = r'([0-9０-９\.,，]+)([^0-9０-９\.,，][^0-9０-９]*)([0-9０-９]{1,2})([^0-9０-９]*)'

    def validate(self, vin):
        m = re.fullmatch(NumUnitDecimal.INPUT_RE, vin)
        if m is None:
            return False
        if re.search(r'[0-9０-９]', m.group(1)) is None:
            return False
        return True

    def _transform(self, vin):
        m = re.match(NumUnitDecimal.INPUT_RE, vin)
        int_part = re.sub(r'[^0-9０-９]', '', m.group(1)) 
        if int_part == '':
            int_part = '0'
        return number_format("%d" % int(int_part) + '.' + "%02d" % int(m.group(3)))

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
        NumUnitDecimal

        )


