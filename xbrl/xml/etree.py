import lxml.etree as etree
from xbrl.qname import parseQName
from xml.sax.saxutils import escape, quoteattr

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
        if tag is not None:
            if type(tag) != set:
                tag = {tag,}
        return (e for e in self if isinstance(e, Element) and (tag is None or e.tag in tag))

    def childElement(self, tag = None):
        return next(self.childElements(tag = tag), None)
        return (e for e in self if isinstance(e, Element) and (tag is None or e.tag == tag))

    @property
    def qnameValue(self):
        return parseQName(self.nsmap, self.text.strip())

    def qnameAttrValue(self, name):
        v = self.get(name, None)
        if v is not None:
            return parseQName(self.nsmap, v.strip())
        return None


    def fragmentToString(self, current_ns = "", include_tag = False):
        """
        A modified serialiser that always uses the default namespace and which
        allows the top-level enclosing tag to be omitted and a default
        namespace assumed.
        """
        if include_tag:
            q = etree.QName(self.tag)
            x = [ q.localname ]
            ns = q.namespace
            if ns is None:
                ns = ""
            if ns != current_ns:
                
                x.append('xmlns=%s' % (quoteattr(ns)))

            s = "<%s>" % (" ".join(x))
        else:
            ns = current_ns
            s = ''

        if self.text is not None:
            s += escape(self.text)

        for e in self:
            if e.tag is not etree.Comment and e.tag is not etree.PI:
                s += e.fragmentToString(current_ns = ns, include_tag = True)
            elif e.tail is not None:
                s += e.tail


        if include_tag:
            s += "</%s>" % q.localname
            if self.tail is not None:
                s += escape(self.tail)

        return s
