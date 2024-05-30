import unittest
import os

from fin.api.fmp import FMPWebAPI

SLOW_TESTS = os.environ.get("SLOW_TESTS")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

class TestFMPWebApi(unittest.TestCase):
    if SLOW_TESTS and FMP_API_KEY:
        def setUp(self):
            self.api = FMPWebAPI(FMP_API_KEY)

        def test_search_name(self):
            result = self.api.search_name(query="Xilam")
            self.assertEqual(result[0]["symbol"], "XIL.PA")



