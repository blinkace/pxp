from . import trrv4 as trrv4
from .trr import TRRegistry, IXTransform, DateTransform
import re

def number_format(x):
    x = re.sub(r'^0+(\d)', r'\1', x)
    x = re.sub(r'\.([^0]*)0+$', r'.\1', x)
    x = re.sub(r'\.$', '', x)
    return re.sub(r'^\.', '0.', x)


class NumDotDecimal(IXTransform):
    name = 'num-dot-decimal'
    INPUT_RE = r'[,\x27\x60\xb4\u2019\u2032 \xa00-9]*(\.[ \xa00-9]+)?'

    def validate(self, vin):
        if re.search(r'[0-9]', vin) is None:
            return False
        return super().validate(vin)

    def _transform(self, vin):
        return number_format(re.sub(r'[^0-9.]','',vin))

class NumUnitDecimal(IXTransform):
    name = 'num-unit-decimal'
    INPUT_RE = r'([0-9０-９\.,，\x27\x60\xB4\u2019\u2032\uFF07]+)([^0-9０-９\.,，\x27\x60\xB4\u2019\u2032\uFF07][^0-9０-９]*)([0-9０-９]{1,2})([^0-9０-９]*)'

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

class NumCommaDecimal(IXTransform):
    name = 'num-comma-decimal'
    INPUT_RE = r'[\.\x27\x60\xb4\u2019\u2032 \xa00-9]*(,[ \xa00-9]+)?'

    def validate(self, vin):
        if re.search(r'[0-9]', vin) is None:
            return False
        return super().validate(vin)

    def _transform(self, vin):
        return number_format(re.sub(r'[^0-9,]','',vin).replace(',','.'))


class TRRv5(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2019-04-19' # XXX

    TRANSFORMS = (
        trrv4.FixedFalse,
        trrv4.FixedTrue,
        trrv4.FixedZero,
        trrv4.FixedEmpty,
        trrv4.DateDayMonth,
        trrv4.DateDayMonthEn,
        trrv4.DateDayMonthYearEn,
        trrv4.DateMonthDay,
        trrv4.DateMonthDayNameEn,
        NumDotDecimal,
        NumCommaDecimal,
        NumUnitDecimal,

        )


