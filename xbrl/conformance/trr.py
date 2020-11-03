from xbrl.xml import parser
import lxml.etree as etree

TEST_CASE_NS = 'http://xbrl.org/2011/conformance-rendering/transforms'

def runTRRTests(path, trr):
    with open(path) as fin:
        tree = etree.parse(fin, parser())

    testsRun = 0
    failures = []
    for test in tree.getroot().childElements(etree.QName(TEST_CASE_NS, 'transform')):
        name = test.qnameAttrValue("name")

        transform = trr.getTransform(name)
        for v in test.childElements(etree.QName(TEST_CASE_NS, "variation")):
            testsRun += 1
            if transform is None:
                failures.append("Unknown transformation: %s" % name)
            else:
                expectedValid = v.get("result") == 'valid'
                i = v.get("input")
                isValid = transform.validate(i)
                if expectedValid != isValid:
                    failures.append("%s - '%s': Expected %s got %s" % (name, i, "valid" if expectedValid else "invalid", "valid" if isValid else "invalid"))
                    continue
                if expectedValid:
                    out = transform.transform(i)
                    if out != v.get("output"):
                        failures.append("%s - %s: Expected '%s' got '%s'" % (name, i, v.get("output"), out))
                        continue

    return (testsRun, failures)


