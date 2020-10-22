from .trrv1 import TRRv1
from .trrv2 import TRRv2
from .trrv3 import TRRv3

class TRRCollection:

    def __init__(self):
        self.registries = dict()


    def addRegistry(self, registry):
        self.registries[registry.ns] = registry

    def getTransform(self, name):
        registry = self.registries.get(name.namespace, None)
        if registry is None:
            raise XBRLError("unknownTransformationRegistry", "Unsupported transformation registry: %s" % name.namespace)
        return registry.getTransform(name)

def buildTRRCollection():
    rc = TRRCollection()
    rc.addRegistry(TRRv1())
    rc.addRegistry(TRRv2())
    rc.addRegistry(TRRv3())
    return rc
