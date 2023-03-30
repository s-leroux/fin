"""
Date and time utilities
"""

import time
from datetime import date, datetime, timedelta

from fin.utils.log import console

def asCalendarDateDelta(something):
    """
    Smart convertion to a CalendarDateDelta instance.
    """
    if isinstance(something, CalendarDateDelta):
        return something

    if isinstance(something, dict):
        return CalendarDateDelta(**something)

    console.debug(something)
    raise NotImplementedError(f"Can't convert from {type(something)} to CalendarDateDelta")

# ======================================================================
# Calendar date delta
# ======================================================================
class CalendarDateDelta:
    slots = (
            "_years",
            "_months",
            "_weeks",
            "_days",
            )

    def __init__(self, *, years=0, months=0, weeks=0, days=0):
        self._years = years
        self._months = months
        self._weeks = weeks
        self._days = days

    def __neg__(self):
        return type(self)(
                years=-self._years,
                months=-self._months,
                weeks=-self._weeks,
                days=-self._days)

    def __pos__(self):
        return self

    def __repr__(self):
        return "{}.{}({}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
                self._weeks,
                self._days,
                )

# ======================================================================
# Calendar dates
# ======================================================================
class CalendarDate:
    slots = (
            "_pydate", # The underlying Python date object
            )

    def __init__(self, year, month, day):
        self._pydate = date(year, month, day)

    @staticmethod
    def today():
        return CalendarDate.fromtimestamp(time.time())

    @staticmethod
    def fromtimestamp(timestamp):
        st = time.localtime(timestamp)
        return CalendarDate(st.tm_year, st.tm_mon, st.tm_mday)

    @staticmethod
    def fromisoformat(format_string):
        """
        Parse a string according to YYYY-MM-DD format and return the
        corresponding date object.
        """
        dt = datetime.strptime(format_string, "%Y-%m-%d")
        return CalendarDate(dt.year, dt.month, dt.day)


    def __repr__(self):
        return "{}.{}({}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self.year,
                self.month,
                self.day,
                )

    def __str__(self):
        return self._pydate.strftime("%Y-%m-%d")

    @property
    def year(self):
        return self._pydate.year

    @property
    def month(self):
        return self._pydate.month

    @property
    def day(self):
        return self._pydate.day

    @property
    def timestamp(self):
        return (self._pydate - date(1970, 1, 1)).total_seconds()

    def iter_by(self, interval = None, *, n = None, **kwargs):
        assert n is None or n >= 0
        assert not(interval and kwargs)
        if n is None:
            n = float("inf")
        if interval is None:
            interval = CalendarDateDelta(**kwargs)

        curr = self

        while n > 0:
            n -= 1
            curr = curr+interval
            yield curr

    def __lt__(self, other):
        return self._pydate < other._pydate

    def __eq__(self, other):
        if type(other) != CalendarDate:
            return False
        return self._pydate == other._pydate

    def __hash__(self):
        return self._pydate.__hash__()

    def __add__(self, delta):
        """
        Create a new CalendarDate offsetted by delta.

        Delta are applied individually from the largest to the smallest unit.
        This may raise a ValueError if the date does not exist or is ambiguous.

        For example, trying to find the calendar date one year before 2020-02-29
        is ambiguous and will raise ValueError (since 2020 is a bisextile year,
        whereas 2019 isn't)
        """
        if isinstance(delta, CalendarDateDelta):
            a,b = divmod((delta._years or 0)*12 + (delta._months or 0), 12)
            new_year = self.year + a
            new_month = self.month + b
            # Above, self.month in the [1..12] range and 12 > b >= 0
            if new_month > 12:
                new_year += 1
                new_month -= 12

            # for days, we can delegate to the python datetime module
            days = delta._weeks*7 + delta._days
            new_date = date(new_year, new_month, self.day) + timedelta(days=days)

            return CalendarDate(
                    new_date.year,
                    new_date.month,
                    new_date.day,
                    )

        return NotImplemented

    def __sub__(self, other):
        """
        Substract a CalendarDateDelta from the current date and retrun the newly created
        CalendarDate instance.
        """
        if isinstance(other, CalendarDateDelta):
            return self + -other

        return NotImplemented

def parseisodate(datestring):
    return CalendarDate.fromisoformat(datestring)
