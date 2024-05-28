import unittest
import os

from fin.api.fmp import FMPRestAPI

SLOW_TESTS = os.environ.get("SLOW_TESTS")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

class TestFMPApi(unittest.TestCase):
    if SLOW_TESTS and FMP_API_KEY:
        def setUp(self):
            self.api = FMPRestAPI(FMP_API_KEY)

        def test_search_name(self):
            result = self.api.search_name(query="Xilam")
            self.assertEqual(result.status_code, 200)
            print(result.json())



