import unittest
import os

from fin.api import yf, cache
from fin.datetime import CalendarDate, CalendarDateDelta

class TestCache(unittest.TestCase):
    def setUp(self):
        self.client = cache.Client(yf.Client(), db_name=":memory:")
        self.ticker = "MCD"

    if os.environ.get('SLOW_TESTS'):
        def test_historical_data(self):
            end = CalendarDate.fromisoformat("2023-03-31")
            duration = CalendarDateDelta(weeks=5)

            t1 = self.client.historical_data(self.ticker, duration, end)
            t2 = self.client.historical_data(self.ticker, duration, end)

            for a, b in zip(t1, t2):
                self.assertEqual(a,b)
