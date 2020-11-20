class TableTemplate:

    def __init__(self, name, columns, dimensions):
        self.name = name
        self.columns = columns
        self.dimensions = dimensions
        for c in self.columns.values():
            c.template = self
        self.report = None



