from collections import namedtuple

TestCaseInput = namedtuple("TestCaseInput", "url, type, readMeFirst")

class TestCase:

    def __init__(self, url, name, description, variations = []):
        self.url = url
        self.name = name
        self.description = description
        self.variations = variations

    def addVariation(self, v):
        self.variations.append(v)

    def __repr__(self):
        return "Name: %s\nDescription: %s\n" % (self.name, self.description)

