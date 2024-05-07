import unittest
import os

from testing import assertions

from fin.api import yf, cache
from fin.datetime import CalendarDate, CalendarDateDelta, parseisodate

class TestCache(unittest.TestCase, assertions.ExtraTests):
    def setUp(self):
        self.client = cache.Client(yf.Client(), db_name=":memory:")
        self.ticker = "MCD"

    if os.environ.get('SLOW_TESTS'):
        def test_historical_data(self):
            end = parseisodate("2023-03-31")
            duration = CalendarDateDelta(weeks=5)

            t1 = self.client.historical_data(self.ticker, duration, end)
            t2 = self.client.historical_data(self.ticker, duration, end)

            # Compare string representation as we may have rounding errors
            # beyond the precision
            self.assertSerieEqual(t1, t2)
