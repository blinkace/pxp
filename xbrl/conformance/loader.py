from lxml import etree
from xbrl.xml import parser
from .testcase import TestCase, TestCaseInput
from .variation import Variation

class SuiteLoader:

    def __init__(self, processor):
        self.processor = processor

    def load(self, url):
        with self.processor.resolver.open(url) as src:
            tree = etree.parse(src, parser())
            root = tree.getroot()
            if etree.QName(root.tag).localname == 'testcase':
                return self.parseTestCase(url, root)


    def parseTestCase(self, url, testCaseElement):
        tc = TestCase(url, testCaseElement.get("name"), testCaseElement.get("description"))
        for v in testCaseElement.iter("{*}variation"):
            desc = v.findtext("{*}description")
            vid = v.get("id")
            name = v.get("name")
            data = v.find("{*}data")
            inputs = [
                    TestCaseInput(c.text, etree.QName(c.tag).localname, c.get("readMeFirst", "false") == "true") for c in data.childElements()
                    ]
            errors = {
                    c.qnameValue for c in v.find("{*}result").findall("{*}error")
                    }
            tc.addVariation(Variation(vid, name, desc, inputs, errors))
        return tc





