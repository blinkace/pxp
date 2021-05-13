class Variation:

    def __init__(self, vid, name, description, inputs = None, errors = None):
        self.id = vid
        self.name = name
        self.description = description
        self.inputs = inputs if inputs is not None else []
        self.errors = errors if errors is not None else {}


    @property
    def readmeFirstInputs(self):
        return list(i for i in self.inputs if i.readMeFirst)

    @property
    def isTaxonomyPackageInput(self):
        return all(i.type == 'taxonomyPackage' for i in self.readmeFirstInputs)


