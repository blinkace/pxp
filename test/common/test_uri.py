from xbrl.common.uri_validate import encodeXLinkURI
import unittest

class URITests(unittest.TestCase):

    def test_xlink_encode(self):

        tests = [
            ["https://www.example.com", "https://www.example.com"],
            ["https://www.example.com/%20foo", "https://www.example.com/%20foo"],
            ["https://www.example.com/%20 foo", "https://www.example.com/%20%20foo"],
            ["https://www.example.com/~foo", "https://www.example.com/~foo"],
            ["https://[::1]/", "https://[::1]/"],
            ["https://www.example.com/á£", "https://www.example.com/%C3%A1%C2%A3"],
            ["https://www.example.com/#foo", "https://www.example.com/#foo"],
        ]

        for (uri_in, uri_out) in tests:
            assert encodeXLinkURI(uri_in) == uri_out

