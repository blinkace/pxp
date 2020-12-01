from .values import ParameterReference
from .column import FactColumn

class TableTemplate:

    def __init__(self, name, columns, properties, rowIdColumn):
        self.name = name
        self.columns = columns
        self.properties = properties
        for c in self.columns.values():
            c.template = self
        self.report = None
        self.rowIdColumn = rowIdColumn

    @property
    def parameterValueColumns(self):
        parameterValueColumns = []
        srcs = [ c.properties for c in self.columns.values() if isinstance(c, FactColumn) ] + [self.properties, self.report.properties]
        for src in srcs:
            for d in list(src.dimensions.values()) + [ src.decimals ]:
                if isinstance(d, ParameterReference) and d.name in self.columns:
                    parameterValueColumns.append(self.columns[d.name])
        return parameterValueColumns

                    




