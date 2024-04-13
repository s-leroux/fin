"""
Core API interfaces
"""
from fin.datetime import CalendarDate, CalendarDateDelta, asCalendarDateDelta
from fin.seq import fc

class HistoricalData:
    def historical_data(self, ticker, duration=CalendarDateDelta(years=1), end=None,* , select=None, adjusted=False):
        """
        Return the historical data corresponding to the parameters as a fin.seq.Table
        instance.

        The default for duration is one year.
        The default for end (the end date) is today.

        The returned table will have the folling columns (order is not garanteed):
        * `Date`
        * `Open`
        * `High`
        * `Low`
        * `Close`
        * `Adj Close`
        * `Volume`

        If you ask for adjusted prices for split/dividens, the returned data will only
        contains the followeing columns:
        * `Date`: as above
        * `Open`: price adjusted for stock split and dividends
        * `High`: price adjusted for stock split and dividends
        * `Low`: price adjusted for stock split and dividends
        * `Close`: as `Adj Close` above
        """
        duration = asCalendarDateDelta(duration)
        if end is None:
            end = CalendarDate.today()
        t = self._historical_data(ticker, duration, end)

        if adjusted:
            t = t.select(
                    "Date",
                    ( fc.adj, "Open", "High", "Low", "Close", "Adj Close" ),
                )

#        if select:
#            t = t.select(*select)

        return t
