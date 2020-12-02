

class PropertyGroupMergeDecimalsConflict(Exception):
    pass

class PropertyGroupMergeDimensionsConflict(Exception):

    def __init__(self, dimension):
        self.dimension = dimension

class Properties:

    def __init__(self, decimals = None, dimensions = None):
        self.decimals = decimals
        self.dimensions = dimensions if dimensions is not None else {}

    # Merge in the properties from another properties object, optionally
    # raising an exception if the property is already defined
    def add(self, other, raiseOnConflict = False):
        if other.decimals is not None:
            if self.decimals is not None and raiseOnConflict:
                raise PropertyGroupMergeDecimalsConflict()
            self.decimals = other.decimals
        for k, v in other.dimensions.items():
            if k in self.dimensions and raiseOnConflict:
                raise PropertyGroupMergeDimensionsConflict(k)
            self.dimensions[k] = v

    def __repr__(self):
        s = "decimals: %s, " % self.decimals
        s += "dimensions: {%s}" % (",".join(("%s: %s" % (str(k), str(v)) for k, v in self.dimensions.items())))
        return s

