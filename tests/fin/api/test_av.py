import unittest
import os

from fin.api.av import AlphaVantageWebAPI, Client
from tests.fin.api import HistoricalDataTest

SLOW_TESTS = os.environ.get("SLOW_TESTS")
AV_API_KEY = os.environ.get("AV_API_KEY")

class TestAlphaVantageApi(unittest.TestCase):
    if SLOW_TESTS and AV_API_KEY:
        def setUp(self):
            self.api = AlphaVantageWebAPI(AV_API_KEY)

        def test_search_name(self):
            result = self.api.symbol_search(keywords="Xilam")
            print(result)

        def test_inflation(self):
            result = self.api.inflation()
            print(result)

if AV_API_KEY:
    class TestAVHistoricalData(HistoricalDataTest, unittest.TestCase):
        def setUp(self):
            self.client = Client(AV_API_KEY)
            self.ticker = "AAPL"

