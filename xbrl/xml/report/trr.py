
class IXTransform:
    pass


class TRRegistry:


    def __init__(self):

        self.transforms = dict()
        for c in type(self).TRANSFORMS:
            self.transforms[c.__name__.lower()] = c()

    @property
    def ns(self):
        return type(self).NAMESPACE

    def getTransform(self, name):
        if name.namespace != self.ns:
            return None

        return self.transforms.get(name.localname, None)

