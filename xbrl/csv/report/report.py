class Report:

    def __init__(self, templates, dimensions, parameters, nsmap, tables):
        self.templates = templates
        for t in self.templates.values():
            t.report = self
        self.parameters = parameters
        self.nsmap = nsmap
        self.tables = tables
        self.dimensions = dimensions

    def loadTables(self, resolver):
        for t in self.tables:
            t.loadData(resolver)
