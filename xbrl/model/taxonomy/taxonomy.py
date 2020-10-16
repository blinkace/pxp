from .concept import Concept

class Taxonomy:

    def __init__(self):
        self.concepts = dict()

    def addConcept(self, c):
        self.concepts[c.name] = c




