import lxml.etree as etree
from xbrl.qname import parseQName
import xml.sax.saxutils as saxutils 

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

    def boolAttrValue(self, name, default = False):
        v = self.get(name, None)
        if v is None:
            return default
        v = v.strip()
        return v in ["1", "true"]

    def fragmentToString(self, current_ns = "", include_tag = False, escape = False):
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
                
                x.append('xmlns=%s' % (saxutils.quoteattr(ns)))

            s = "<%s>" % (" ".join(x))
        else:
            ns = current_ns
            s = ''

        if self.text is not None:
            s += saxutils.escape(self.text)

        if escape:
            s = saxutils.escape(s)

        for e in self:
            if e.tag is not etree.Comment and e.tag is not etree.PI:
                s += e.fragmentToString(current_ns = ns, include_tag = True)
            elif e.tail is not None:
                s += e.tail


        if include_tag:
            t = "</%s>" % q.localname
            if self.tail is not None:
                t += saxutils.escape(self.tail)
            if escape:
                t = saxutils.escape(t)
            s += t

        return s
