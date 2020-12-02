from .validators import isValidIdentifier
from xbrl.xbrlerror import XBRLError

class Parameters:

    def __init__(self, initial = None):
        if initial is None:
            initial = dict()

        self.parameters = initial
        self.used = set()
        for k in initial:
            if not isValidIdentifier(k):
                raise XBRLError("xbrlce:invalidIdentifier", "%s is not a valid parameter name" % k)

    def __setitem__(self, k, v):
        if not isValidIdentifier(k):
            raise XBRLError("xbrlce:invalidIdentifier", "%s is not a valid parameter name" % k)
        self.parameters[k] = v

    def __contains__(self, k):
        return k in self.parameters

    def get(self, k, default = None):
        return self.parameters.get(k, default)

    def getAndUse(self, k, default = None):
        if k in self:
            self.used.add(k)
        return self.get(k, default)

    def unused(self):
        return set(self.parameters.keys()) - self.used





