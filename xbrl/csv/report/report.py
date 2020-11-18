class Report:

    def __init__(self, templates, dimensions, parameters, nsmap, tables):
        self.templates = templates
        self.parameters = parameters
        self.nsmap = nsmap
        self.tables = tables

    def loadTables(self, resolver):
        for t in self.tables:
            t.loadData(resolver)
