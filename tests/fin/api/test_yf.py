import unittest
from fin.api import yf

class TestUtilities(unittest.TestCase):
    def test_get(self):
        """ The get() method should insert a well known user agent in the headers
        """
        ua = ""

        def trace(*args, headers={}):
            nonlocal ua
            ua = headers['User-Agent']

        r = yf.get("http://www.google.com", _get=trace)
        self.assertRegex(ua, "Mozilla")

class TestYF(unittest.TestCase):
    def test_x(self):
        self.assertTrue(False)
