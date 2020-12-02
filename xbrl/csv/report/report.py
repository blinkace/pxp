from xbrl.model.report import Report

class CSVReport:

    def __init__(self, templates, properties, parameters, nsmap, tables, taxonomy, allowedDuplicates):
        self.templates = templates
        for t in self.templates.values():
            t.report = self
        self.parameters = parameters
        self.nsmap = nsmap
        self.tables = tables
        self.properties = properties
        self.taxonomy = taxonomy
        self.allowedDuplicates = allowedDuplicates

    def loadTables(self, resolver):
        facts = set()
        for t in self.tables:
            facts.update(t.loadData(resolver))
        return facts
        
