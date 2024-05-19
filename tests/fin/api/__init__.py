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
            dc = t["Date"].columns[-1]
            self.assertStartsWith(str(dc[-1]), "2023-01-03")
            self.assertStartsWith(str(dc[0]), "2022-12-28")
            # self.assertEqual(len(dc), 5) # some exchange are open the week-end!
            for cell in dc:
                self.assertIsInstance(cell, CalendarDate)
                self.assertGreaterEqual(str(cell), "2022-12-28")
                self.assertLess(str(cell), "2023-01-04")


