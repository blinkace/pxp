from .values import ExplicitNoValue

class Column:

    def __init__(self, name):
        self.name = name
        pass

class PropertyGroupColumn(Column):

    def __init__(self, name, propertyGroups):
        super().__init__(name)
        self.propertyGroups = propertyGroups


class FactColumn(Column):

    def __init__(self, name, properties, propertiesFrom):
        super().__init__(name)
        self.properties = properties
        self.template = None
        self.propertiesFrom = propertiesFrom

    def getEffectiveDimensions(self, propertyGroupProperties):
        dims = dict()
        for dimSet in (self.template.report.properties.dimensions, self.template.properties.dimensions, propertyGroupProperties.dimensions, self.properties.dimensions):
            for k, v in dimSet.items():
                if isinstance(v, ExplicitNoValue):
                    dims.pop(k)
                else:
                    dims[k] = v

        return dims

    def getEffectiveDecimals(self, propertyGroupProperties):
        for d in (self.template.report.properties.decimals, self.template.properties.decimals, propertyGroupProperties.decimals, self.properties.decimals):
            if d is not None:
                return d

        return None

