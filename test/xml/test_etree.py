import xbrl.xml
import lxml.etree as etree


XML = """
<root>
   <a>aa</a>
   <!-- a comment -->
   <b>bb</b>
</root>
"""

def test_custom_element_class():
    root = etree.fromstring(XML, xbrl.xml.parser())
    assert len(root) == 3

    for e in root:
        print(type(e))

    assert len(list(root.childElements())) == 2
    assert len(list(root.childElements(tag = 'a'))) == 1

