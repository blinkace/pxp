class Variation:

    def __init__(self, vid, name, description, inputs = [], errors = {}):
        self.id = vid
        self.name = name
        self.description = description
        self.inputs = inputs
        self.errors = errors
