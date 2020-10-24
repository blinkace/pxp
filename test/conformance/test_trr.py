from xbrl.xml.report import TRRv2, TRRv3
from xbrl.conformance.trr import runTRRTests
import os.path


def test_trrv3_conformance():
    (testsRun, failures) = runTRRTests(os.path.join(os.path.dirname(__file__), "trrv3", "tests.xml"), TRRv3())
    assert testsRun > 0
    for failure in failures:
        print(failure) 
    assert len(failures) <= 100

def test_trrv2_conformance():
    (testsRun, failures) = runTRRTests(os.path.join(os.path.dirname(__file__), "trrv2", "tests.xml"), TRRv2())
    assert testsRun > 0
    for failure in failures:
        print(failure) 
    assert len(failures) == 0


