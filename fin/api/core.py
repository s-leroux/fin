"""
Core API interfaces
"""
from fin.datetime import CalendarDate, CalendarDateDelta, asCalendarDateDelta, asCalendarDate

class HistoricalData:
    def historical_data(self, ticker, duration=CalendarDateDelta(years=1), end=None,* , select=None):
        """
        Return the historical data corresponding to the parameters as a fin.seq.Table
        instance.

        The default for duration is one year.
        The default for end (the end date) is today.

        The returned table will have the folling columns (order is not garanteed):
        * `Data`
        * `Open`
        * `High`
        * `Low`
        * `Close`
        * `Adj Close`
        * `Volume`
        """
        duration = asCalendarDateDelta(duration)
        if end is None:
            end = CalendarDate.today()
        else:
            end = asCalendarDate(end)
        t = self._historical_data(ticker, duration, end)

#        if select:
#            t = t.select(*select)

        return t
