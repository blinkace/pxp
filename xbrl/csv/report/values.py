from collections import namedtuple
import re

from xbrl.xbrlerror import XBRLError

from .validators import isValidIdentifier

class ExplicitNoValue:
    pass

class ParameterReference:

    def __init__(self, name, periodSpecifier):
        self.name = name
        self.periodSpecifier = periodSpecifier

class RowNumberReference:
    pass

def parseReference(name):
    assert name.startswith("$")

    if name == '$rowNumber':
        return RowNumberReference()
    elif '@' in name:
        (ref, periodSpecifier) = name.split('@', 2)
        if periodSpecifier not in {"start", "end"}:
            raise XBRLError("xbrlce:invalidPeriodSpecifier", "'%s' is not a valid period specifier (%s).  Must be 'start' or 'end'" % (periodSpecifier, name))
    else:
        (ref, periodSpecifier) = (name, None)

    ref = ref[1:]

    if not isValidIdentifier(ref):
        raise XBRLError("xbrlce:invalidReference", "'$%s' is not a valid row number reference or parameter reference" % name)

    return ParameterReference(ref, periodSpecifier)


def parseNumericValue(v, defaultDecimals):
    d = defaultDecimals
    if v is None:
        return (v, d)
    if 'd' in v:
        (num, dec) = v.split('d', 2)

        if num != num.rstrip():
            raise XBRLError("xbrlce:invalidDecimalsSuffix", "Space is not permitted before a decimals suffix (value: %s)" % (v))
        
        if re.match(r'^(0|-?[1-9][0-9]*|INF)$', dec) is None:
            raise XBRLError("xbrlce:invalidDecimalsSuffix", "%s is not a valid decimals suffix (value: %s)" % (dec, v))

        if dec == "INF":
            return (num, None)
        d = int(dec)
    else:
        num = v

    try:
        float(num)
    except ValueError:
        raise XBRLError("xbrlce:invalidFactValue", "%s is not a valid numeric value" % (num))
        
    return (num, d)


class NotPresentClass:
    pass

NotPresent = NotPresentClass()


