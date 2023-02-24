"""
Date and time utilities
"""

from datetime import date, datetime, timedelta

# ======================================================================
# Calendar date delta
# ======================================================================
class CalendarDateDelta:
    slots = (
            "_years",
            "_months",
            "_days",
            )

    def __init__(self, years=None, months=None, days=None):
        self._years = years
        self._months = months
        self._days = days

    def __neg__(self):
        return type(self)(-self._years, -self._months, -self._days)

    def __pos__(self):
        return self

    def __repr__(self):
        return "{}.{}({}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
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

    def __lt__(self, other):
        return self._pydate < other._pydate

    def __eq__(self, other):
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
            new_date = date(new_year, new_month, self.day) + timedelta(days=delta._days or 0)

            return CalendarDate(
                    new_date.year,
                    new_date.month,
                    new_date.day,
                    )

        return NotImplemented

def parseisodate(datestring):
    """
    Parse a string according to YYYY-MM-DD format and return the
    corresponding date object.
    """
    dt = datetime.strptime(datestring, "%Y-%m-%d")
    return CalendarDate(dt.year, dt.month, dt.day)
    
