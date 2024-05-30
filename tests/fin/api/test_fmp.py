import unittest
import os
import json

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

        def test_historical_price_full(self):
            result = self.api.historical_price_full(**{
                    "symbol": "AAPL",
                    "from": "2023-01-21",
                    "to": "2023-02-22",
                    })
            with open("tests/_fixtures/AAPL-20230121-20230222.json", "rt") as f:
                # json.dump(result, f, indent=4)
                expected = json.load(f)
            self.assertEqual(result, expected)



