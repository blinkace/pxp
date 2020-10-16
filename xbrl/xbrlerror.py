from lxml import etree
from .const import NS, PREFIX

class XBRLError(Exception):

    def __init__(self, code, message, spec_ref = None):
        if ':' in code:
            (prefix, localpart) = code.split(':')
        else:
            (prefix, localpart) = ("pyxbrle", code)

        self.code = etree.QName(NS[prefix], localpart)
        self.message = message
        self.spec_ref = spec_ref

    @property
    def code_as_qname(self):
        return "%s:%s" % (PREFIX[self.code.namespace], self.code.localname)

        




