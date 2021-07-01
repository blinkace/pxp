from xbrl.common import isValidLanguageCode
from xbrl import XBRLError
import unittest

class LanguageCodeTests(unittest.TestCase):

    def test_languageCodes(self):

        passes = (
            "en-GB",
            "en",
            "x-klingon",
            "i-hak",
        )

        for lang in passes:
            assert isValidLanguageCode(lang)

        fails = (
            "1234",
            "en-us-zz-zz-zz-zz-zz",
            " en ",
        )

        for f in fails:
            assert not isValidLanguageCode(f)
