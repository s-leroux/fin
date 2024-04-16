import os
import unittest

from fin.api.yf import Client
from tests.fin.api import HistoricalDataTest
from fin.datetime import CalendarDate, CalendarDateDelta, parseisodate

class TestYF(HistoricalDataTest, unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.ticker = "MCD"

    if os.environ.get('SLOW_TESTS'):
        def test_historical_data_chunked(self):
            """
            Check we can overcome the one-year maximum historical data download
            limit on Yahoo! Finance.
            """
            params=dict(
                end = parseisodate("2023-01-03"),
                duration = CalendarDateDelta(years=3),
                )

            t = self.client.historical_data(self.ticker, **params)

            dc = t["Date"].columns[-1]
            self.assertEqual(str(dc[0]), "2020-01-03")
            self.assertEqual(str(dc[-1]), "2023-01-03")
            self.assertEqual(len(dc), 756)
            with open("tests/_fixtures/MCD-20200103-20230103.csv", "rt") as f:
                line_no = 1
                for actual, expected in zip(t.as_csv().splitlines(), f):
                    actual = actual.strip()
                    expected = expected.strip()
                    #
                    # Below:
                    # Check only the first characters of each line since apparently
                    # the price can vary by +/-0.01 depending the Yahoo server (?!?)
                    #
                    # i.e.:
                    # AssertionError: '[...], 170.75, 2399600' != '[...], 170.74, 2399600'
                    # - 2020-07-07, 187.37, 187.85, 185.25, 185.82, 170.75, 2399600
                    # ?                                                  ^
                    # + 2020-07-07, 187.37, 187.85, 185.25, 185.82, 170.74, 2399600
                    # ?                                                  ^
                    #  : line 129
                    self.assertEqual(actual[:16], expected[:16], msg=f"line {line_no}")
                    line_no += 1

