class Report:

    def __init__(self, taxonomy):
        self.facts = dict()
        self.taxonomy = taxonomy

    def addFact(self, fact):
        self.facts[fact.id] = fact
        fact.report = self

