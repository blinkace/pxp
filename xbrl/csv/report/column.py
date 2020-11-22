from .values import ExplicitNoValue

class Column:

    def __init__(self, name):
        self.name = name
        pass

class PropertyGroupColumn(Column):

    pass


class FactColumn(Column):

    def __init__(self, name, dimensions, propertiesFrom):
        super().__init__(name)
        self.dimensions = dimensions
        self.template = None
        self.propertiesFrom = propertiesFrom

    def getEffectiveDimensions(self):
        dims = dict()
        for dimSet in (self.template.report.dimensions, self.template.dimensions, self.dimensions):
            for k, v in dimSet.items():
                if isinstance(v, ExplicitNoValue):
                    dims.pop(k)
                else:
                    dims[k] = v

        return dims

