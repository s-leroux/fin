"""
Core set of test usable on all API
"""
import os

from testing.assertions import ExtraTests

from fin.datetime import CalendarDate, CalendarDateDelta, parseisodate

class HistoricalDataTest(ExtraTests):
    if os.environ.get('SLOW_TESTS'):
        def test_historical_data_columns(self):
            """
            The historical_data() method should return the 6 standard columns for
            end-of-day data.
            """
            t = self.client.historical_data(self.ticker)
            headings = t.headings
            for heading in ('Date', 'Open', 'High', 'Low', 'Close', 'Volume'):
                self.assertIn(heading, headings)

        def test_historical_data_start_end(self):
            """
            The historical_data() method should honnor the `end` and `duration` parameters.
            """
            params=dict(
                end = parseisodate("2023-01-03"),
                duration = CalendarDateDelta(weeks=1),
                )

            t = self.client.historical_data(self.ticker, **params)
            datefmt = "%Y-%m-%d"
            dc = t["Date"].data[-1]
            self.assertStartsWith(dc[-1].format(datefmt), "2023-01-03")
            self.assertStartsWith(dc[0].format(datefmt), "2022-12-28")
            # self.assertEqual(len(dc), 5) # some exchange are open the week-end!
            for cell in dc:
                self.assertIsInstance(cell, CalendarDate, msg=str(type(cell)))
                self.assertGreaterEqual(str(cell), "2022-12-28")
                self.assertLess(str(cell), "2023-01-04")


