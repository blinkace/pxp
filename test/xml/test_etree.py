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


XML_WITH_LANG = """
<root>
   <a xml:lang="en-US">
    <c xml:lang="en-GB" />
    <d />
   </a>
   <b>bb</b>
</root>
"""

def test_xml_lang():
    root = etree.fromstring(XML_WITH_LANG, xbrl.xml.parser())
    assert(root.xpath("//root")[0].effectiveLang() is None)
    assert(root.xpath("//a")[0].effectiveLang() == 'en-US')
    assert(root.xpath("//c")[0].effectiveLang() == 'en-GB')
    assert(root.xpath("//d")[0].effectiveLang() == 'en-US')
    assert(root.xpath("//b")[0].effectiveLang() is None)


