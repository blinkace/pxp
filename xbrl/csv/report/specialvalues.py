from xbrl.xbrlerror import XBRLError
from .values import ExplicitNoValue

def processSpecialValues(value, allowNone = True):
    if value == "#empty":
        return ""
    elif value == '#nil':
        return None
    elif value == '#none':
        if not allowNone:
            raise XBRLError("xbrlce:illegalUseOfNone", "Illegal use of none")
        return ExplicitNoValue()
    elif value.startswith('##'):
        return value[1:]
    elif value.startswith('#'):
        raise XBRLError("xbrlce:unknownSpecialValue", '"%s" is an unknown special value (must be "#empty", "#nil" or "#none")' % value)
    return value


