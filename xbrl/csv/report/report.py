class Report:

    def __init__(self, templates, properties, parameters, nsmap, tables, taxonomy):
        self.templates = templates
        for t in self.templates.values():
            t.report = self
        self.parameters = parameters
        self.nsmap = nsmap
        self.tables = tables
        self.properties = properties
        self.taxonomy = taxonomy

    def loadTables(self, resolver):
        for t in self.tables:
            t.loadData(resolver)
