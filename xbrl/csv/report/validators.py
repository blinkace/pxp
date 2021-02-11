from xbrl.xbrlerror import XBRLError
from xbrl.common import RE_NCNAME

def isValidIdentifier(i):
    return RE_NCNAME.match(i) is not None and "." not in i



