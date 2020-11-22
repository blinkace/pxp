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

    if name == '$rowNumber':
        return RowNumberReference()
    elif '@' in name:
        (ref, periodSpecifier) = name.split(name, 2)
        if periodSpecifier not in {"start", "end"}:
            raise XBRLError("xbrlce:invalidPeriodSpecifier", "'%s' is not a valid period specified.  Must be 'start' or 'end'" % periodSpecifier)
    else:
        (ref, periodSpecifier) = (name, None)

    assert ref.startswith("$")
    ref = ref[1:]

    if not isValidIdentifier(ref):
        raise XBRLError("xbrlce:invalidReference", "'$%s' is not a valid row number reference or parameter reference" % name)

    return ParameterReference(ref, periodSpecifier)


