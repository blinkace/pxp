from .validators import isValidIdentifier
from xbrl.xbrlerror import XBRLError

class Parameters(dict):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        for k in self.keys():
            if not isValidIdentifier(k):
                raise XBRLError("xbrlce:invalidIdentifier", "%s is not a valid parameter name" % k)


    def __setitem__(self, k, v):
        if not isValidIdentifier(k):
            raise XBRLError("xbrlce:invalidIdentifier", "%s is not a valid parameter name" % k)
        super().__setitem__(k, v)

