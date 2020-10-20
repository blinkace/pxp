from .trr import TRRegistry, IXTransform
import re

class IXNumDotDecimal(IXTransform):

    NAME = 'numdotdecimal'

    def transform(self, vin):
        return re.sub(r'[^0-9.]','',vin)

class IXNumCommaDecimal(IXTransform):

    NAME = 'numcommadecimal'

    def transform(self, vin):
        return re.sub(r'[^0-9,]','',vin).replace(',','.')


class TRRv3(TRRegistry):

    NAMESPACE = 'http://www.xbrl.org/inlineXBRL/transformation/2015-02-26'

    TRANSFORMS = (
        IXNumCommaDecimal,
        IXNumDotDecimal,
    )


