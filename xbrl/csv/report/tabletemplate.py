class TableTemplate:

    def __init__(self, name, columns, properties):
        self.name = name
        self.columns = columns
        self.properties = properties
        for c in self.columns.values():
            c.template = self
        self.report = None



