import lxml.etree as etree

def parser():
    parser_lookup = etree.ElementDefaultClassLookup(element=Element)
    parser = etree.XMLParser()
    parser.set_element_class_lookup(parser_lookup)
    return parser


class Element(etree.ElementBase):

    @property
    def iselement(self):
        return self.tag is not etree.Comment and self.tag is not etree.PI

    def childElements(self, tag = None):
        return (e for e in self if isinstance(e, Element) and (tag is None or e.tag == tag))

    def childElement(self, tag = None):
        return next(self.childElements(tag = tag), None)
        return (e for e in self if isinstance(e, Element) and (tag is None or e.tag == tag))