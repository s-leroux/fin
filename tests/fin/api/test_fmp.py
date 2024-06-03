import unittest
import os
import json

from fin.api.fmp import FMPWebAPI, Client
from tests.fin.api import HistoricalDataTest

SLOW_TESTS = os.environ.get("SLOW_TESTS")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

class TestFMPWebApi(unittest.TestCase):
    if SLOW_TESTS and FMP_API_KEY:
        def setUp(self):
            self.api = FMPWebAPI(FMP_API_KEY)

        def test_search_name(self):
            result = self.api.search_name(query="Xilam")
            self.assertEqual(result[0]["symbol"], "XIL.PA")

        def test_stock_list(self):
            result = self.api.stock_list()
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 80000)
            for field in "symbol", "exchange", "name":
                self.assertIn(field, result[0])

        def test_etf_list(self):
            result = self.api.etf_list()
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 10000)
            for field in "symbol", "exchange", "name":
                self.assertIn(field, result[0])

        def test_financial_statement_symbol_lists(self):
            result = self.api.financial_statement_symbol_lists()
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 60000)
            self.assertIn("AAPL", result)

        def test_cash_flow_statement(self):
            result = self.api.cash_flow_statement(**{
                    "symbol": "AAPL",
                    "limit": 4,
                    "period": "quaterly",
                    })
            self.assertEqual(len(result), 4)
            for record in result:
                self.assertEqual(record["symbol"], "AAPL")
                self.assertIn("date", record.keys())
                self.assertIn("netIncome", record.keys())
                self.assertIn("freeCashFlow", record.keys())

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

if FMP_API_KEY:
    class TestFMPHistoricalData(HistoricalDataTest, unittest.TestCase):
        def setUp(self):
            self.client = Client(FMP_API_KEY)
            self.ticker = "AAPL"


