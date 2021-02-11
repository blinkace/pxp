from xbrl.xbrlerror import XBRLError
from .regex import RE_NCNAME

class InvalidSQName(Exception):
    pass

def parseSQName(sqname, nsmap):

    if ":" not in sqname:
        raise InvalidSQName("%s is not a valid SQName" % sqname)

    (prefix, localname) = sqname.split(":", 1)
    if RE_NCNAME.match(prefix) is None:
        raise InvalidSQName("%s is not a valid SQName (invalid prefix)" % sqname)

    uri = nsmap.get(prefix)
    if uri is None:
        raise XBRLError("oimce:unboundPrefix", "Unknown prefix '%s'" % prefix)
    return uri, localname

