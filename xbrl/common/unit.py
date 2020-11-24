from .regex import RE_QNAME
from xbrl.xbrlerror import XBRLError
from xbrl.xml import qname

import re

def parseMeasureList(usr, s, nsmap):
    measureStrs = s.split('*')
    if measureStrs != sorted(measureStrs):
        raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': measures must be sorted" % (usr))
    measures = []
    for measure in s.split('*'):
        if re.match(RE_QNAME, measure) is None:
            raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': '%s' is not a valid QName" % (usr, measure))
        try:
            measures.append(qname(measure, nsmap))
        except KeyError as e:
            raise XBRLError("oimce:unboundPrefix", "Undeclared namespace prefix (%s)" % measure)

    return measures


def parseHalfUnit(usr, s, nsmap):
    m = re.match('^\((.*)\)$', s)
    if m is not None:
        s = m.group(1)
        if '*' not in s:
            raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': parentheses must only be used if more than one measure present in numerator or denominator." % (usr))
    elif '*' in s:
        raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': numerator or denominator with more than one measure must be in parentheses." % (usr))

    return parseMeasureList(usr, s, nsmap)


def parseUnitString(usr, nsmap):
    if re.search(r'\s', usr) is not None:
        # This is redundant but enables a more helpful error message.
        raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': unit strings must not contain whitespace" % (usr))

    if '/' in usr:
        (numStr, denomStr) = usr.split('/', 2)
        nums = parseHalfUnit(usr, numStr, nsmap)
        denoms = parseHalfUnit(usr, denomStr, nsmap)
    else:
        if usr.strip().startswith('('):
            raise XBRLError("oimce:invalidUnitStringRepresentation", "Invalid unit string '%s': Parentheses must only be used if a denominator is present." % (usr))
        nums = parseMeasureList(usr, usr, nsmap)
        denoms = []
        
    return (nums, denoms)

    
