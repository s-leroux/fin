"""
Date and time utilities
"""

import time
from datetime import date, datetime, timedelta, timezone

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

def asCalendarDate(something):
    """
    Smart convertion to a CalendarDate instance.
    """
    if isinstance(something, CalendarDate):
        return something

    if isinstance(something, str):
        return parseisodate(something)

    console.debug(something)
    raise NotImplementedError(f"Can't convert from {type(something)} to CalendarDate")

DATE="DATE"
DATETIME="DATETIME"
DATETIMEMS="DATETIMEMS"

DATE_FORMAT={
    DATE: "%Y-%m-%d",
    DATETIME: "%Y-%m-%dT%H:%M:%S",
    DATETIMEMS: "%Y-%m-%dT%H:%M:%S.%f",
}

# ======================================================================
# Calendar date delta
# ======================================================================
class _CalendarDateDelta:
    """
    Abstract base class for Calendar{Date,Datetime,DateTimeMicro}.

    These classes are designed to express a date relative to another date.
    See _CalendarDate.

    These class only support a limited subset of arithmetic operations as typically
    they are not associative. For example

    ```
    (today + 1 year) + 1 day
    ```
    is not necessarilly the same date as
    ```
    (today + 1 day) + 1 year
    ```

    If the current date is 2023-02-28, the former expression will lead to 2024-02-29
    whereas the latter will be 2024-03-01.
    """
    slots = (
            "_years",
            "_months",
            "_weeks",
            "_days",
            "_hours",
            "_minutes",
            "_seconds",
            "_microseconds",
            "_resolution",
            )

    def __init__(self, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0, resolution):
        if resolution not in DATE_FORMAT:
            raise ValueError(f"Wrong resolution: {resolution}")

        self._years = years
        self._months = months
        self._weeks = weeks
        self._days = days
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds
        self._microseconds = microseconds
        self._resolution = resolution

    def __eq__(self, other):
        """
        Equality is defined in rather strict terms where `delta1 == delta2`
        only is `delta1` is *always* the same as `delta2`.

        For example week and days are interchangeable as one week is always seven days.
        But month and days are not.

        Comparing two deltas with different resolutions raises an error.
        """
        if not isinstance(other, _CalendarDateDelta):
            return False # XXX Shouldn't this raise an exception?

        if self._resolution != other._resolution:
            raise ValueError(f"Cannot mix {self._resolution} and {other._resolution}")

        self_ms = ((((self._weeks*7+self._days)*24+self._hours)*60+self._minutes)*60+self._seconds)*1000000+self._microseconds
        other_ms = ((((other._weeks*7+other._days)*24+other._hours)*60+other._minutes)*60+other._seconds)*1000000+other._microseconds

        return  (self._years == other._years) \
                and (self._months == other._months) \
                and (self_ms == other_ms)

    def __neg__(self):
        cls = type(self)
        result = cls.__new__(cls)
        result._years=-self._years
        result._months=-self._months
        result._weeks=-self._weeks
        result._days=-self._days
        result._hours=-self._hours
        result._minutes=-self._minutes
        result._seconds=-self._seconds
        result._microseconds=-self._microseconds
        result._resolution=self._resolution

        return result

    def __pos__(self):
        return self

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {}, {}, resolution={})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
                self._weeks,
                self._days,
                self._hours,
                self._minutes,
                self._seconds,
                self._microseconds,
                self._resolution,
                )

class CalendarDateDelta(_CalendarDateDelta):
    def __init__(self, *, years=0, months=0, weeks=0, days=0):
        super().__init__(
                years=years, months=months, weeks=weeks, days=days,
                resolution=DATE)

    def __repr__(self):
        return "{}.{}({}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
                self._weeks,
                self._days,
                )

class CalendarDateTimeDelta(_CalendarDateDelta):
    def __init__(self, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        super().__init__(
                years=years, months=months, weeks=weeks, days=days,
                hours=hours, minutes=minutes, seconds=seconds,
                resolution=DATETIME)

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
                self._weeks,
                self._days,
                self._hours,
                self._minutes,
                self._seconds,
                )

class CalendarDateTimeMicroDelta(_CalendarDateDelta):
    def __init__(self, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0):
        super().__init__(
                years=years, months=months, weeks=weeks, days=days,
                hours=hours, minutes=minutes, seconds=seconds,
                microseconds=microseconds,
                resolution=DATETIMEMS)

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self._years,
                self._months,
                self._weeks,
                self._days,
                self._hours,
                self._minutes,
                self._seconds,
                self._microseconds,
                )

# ======================================================================
# Calendar dates
# ======================================================================
class _CalendarDate:
    """
    Calendar date abstract base class.

    Internally, calendar date are stored as a standard Python `datetime` object
    with timezone set to UTC. All input parameters are assumed to be expressed as UTC.
    """
    DATE=DATE
    DATETIME=DATETIME
    DATETIMEMS=DATETIMEMS

    slots = (
            "_pydate",    # The underlying Python date object
            "_resolution",      # Kind of date (date/datetime/datetimems)
            )

    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, *, resolution):
        if resolution not in DATE_FORMAT:
            raise ValueError(f"Wrong resolution: {resolution}")

        self._pydate = datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)
        self._resolution = resolution

    @staticmethod
    def fromtimestamp(timestamp, resolution):
        dt = datetime.fromtimestamp(timestamp, timezone.utc)

        if resolution == DATE:
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif resolution == DATETIME:
            dt = dt.replace(microsecond=0)
        elif resolution == DATETIMEMS:
            pass
        else:
            raise ValueError("Not a valid resolution: "+str(resolution))

        result = CalendarDate.__new__(CalendarDate)
        result._pydate = dt
        result._resolution = resolution

        return result

    @classmethod
    def fromstring(cls, string, fmt, resolution):
        """
        Parse a string using a `strptime`-compatible format and register it.
        """
        try:
            string = str(string, "utf8") # for binary strings
        except TypeError:
            pass


        dt = datetime.strptime(string, fmt)

        # Convert to UTC
        if dt.tzinfo is None or dt.tzinfo.utcoffset(d) is None:
            # Naive datetime
            # XXX Is it possible for strptime to return a naive datetime?
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Aware datetime
            dt = dt.astimezone(timezone.utc)

        # FIXME Should reduce resolution according to the calendar date resolution

        result = cls.__new__(cls)
        result._pydate = dt
        result._resolution = resolution

        return result

    @staticmethod
    def parser(fmt, resolution):
        def _parser(string):
            return CalendarDate.fromstring(string, fmt, resolution)

        return _parser

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {}, {}, resolution={})".format(
                type(self).__module__,
                type(self).__name__,
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.microsecond,
                self._resolution,
                )

    def __str__(self):
        return self._pydate.strftime(DATE_FORMAT[self._resolution])

    def format(self, fmt):
        return self._pydate.strftime(fmt)

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
    def hour(self):
        return self._pydate.hour

    @property
    def minute(self):
        return self._pydate.minute

    @property
    def second(self):
        return self._pydate.second

    @property
    def microsecond(self):
        return self._pydate.microsecond

    @property
    def timestamp(self):
        return self._pydate.timestamp()

    def iter_by(self, interval = None, *, n = None, **kwargs):
        assert n is None or n >= 0
        assert not(interval and kwargs)
        if n is None:
            n = float("inf")
        if interval is None:
            interval = CalendarDateDelta(**kwargs)

        if self._resolution != interval._resolution:
            raise ValueError(f"Cannot mix {self._resolution} and {interval._resolution}")

        curr = self

        while n > 0:
            n -= 1
            curr = curr+interval
            yield curr

    def __lt__(self, other):
        if self._resolution != other._resolution:
            raise ValueError(f"Cannot mix {self._resolution} and {other._resolution}")

        return self._pydate < other._pydate

    def __eq__(self, other):
        if not isinstance(other, _CalendarDate):
            return False

        if self._resolution != other._resolution:
            raise ValueError(f"Cannot mix {self._resolution} and {other._resolution}")

        return self._pydate == other._pydate

    def __hash__(self):
        return self._pydate.__hash__()

    def __add__(self, delta):
        """
        Create a new CalendarDate offset by delta.

        Delta are applied individually from the largest to the smallest unit.
        This may raise a ValueError if the date does not exist or is ambiguous.

        For example, trying to find the calendar date one year before 2020-02-29
        is ambiguous and will raise ValueError (since 2020 is a leap year,
        whereas 2019 isn't)

        If is a *error* to apply a delta whose resolution in greater than the
        receiving calendar date (ie: add a MICROSECOND resolution delta to a
        DATE resolution calendar date)..
        """
        try:
            delta = asCalendarDateDelta(delta)
        except:
            return NotImplemented

        self_resolution = self._resolution
        delta_resolution = delta._resolution

        if f"{self_resolution}:{delta_resolution}" not in (
                "DATE:DATE",
                "DATETIME:DATETIME", "DATETIME:DATE",
                "DATETIMEMS:DATETIME", "DATETIMEMS:DATE", "DATETIMEMS:DATETIMEMICRO"
                ):
            raise ValueError(f"Cannot mix {self_resolution} and {delta_resolution}")

        a,b = divmod((delta._years or 0)*12 + (delta._months or 0), 12)
        new_year = self.year + a
        new_month = self.month + b
        # Above, self.month in the [1..12] range and 12 > b >= 0
        if new_month > 12:
            new_year += 1
            new_month -= 12

        new_date = self._pydate.replace(year=new_year, month=new_month)

        # for days, we can delegate to the python datetime module
        days = delta._weeks*7 + delta._days
        new_date = new_date + timedelta(days=days)

        microseconds = (((delta._hours*60)+delta._minutes)*60+delta._seconds*1000000)+delta._microseconds
        new_date = new_date + timedelta(microseconds=microseconds)

        cls = type(self)
        result = cls.__new__(cls)
        result._pydate = new_date
        result._resolution=self_resolution

        return result

    def __sub__(self, other):
        """
        Substract a CalendarDateDelta from the current date and retrun the newly created
        CalendarDate instance.
        """
        if isinstance(other, CalendarDateDelta):
            return self + -other

        return NotImplemented

class CalendarDate(_CalendarDate):
    def __init__(self, year, month, day):
        super().__init__(year, month, day, resolution=DATE)

    @staticmethod
    def today():
        """
        Return the current time as a calendar date with *date* resolution.
        """
        return _CalendarDate.fromtimestamp(time.time(), DATE)

    @staticmethod
    def fromtimestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp, timezone.utc)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        result = CalendarDate.__new__(CalendarDate)
        result._pydate = dt
        result._resolution = DATE

        return result

    @classmethod
    def fromstring(cls, string, fmt):
        return super(CalendarDate, cls).fromstring(string, fmt, resolution=DATE)

    def __repr__(self):
        return "{}.{}({}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self.year,
                self.month,
                self.day,
                )

class CalendarDateTime(_CalendarDate):
    def __init__(self, year, month, day, hour=0, minute=0, second=0):
        super().__init__(year, month, day, hour, minute, second, resolution=DATETIME)

    @staticmethod
    def now():
        """
        Return the current time as a calendar date with *datetime* resolution.
        """
        return _CalendarDate.fromtimestamp(time.time(), DATETIME)

    @staticmethod
    def fromtimestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp, timezone.utc)
        dt = dt.replace(microsecond=0)

        result = CalendarDate.__new__(CalendarDate)
        result._pydate = dt
        result._resolution = DATETIME

        return result

    @classmethod
    def fromstring(cls, string, fmt):
        return super(CalendarDateTime, cls).fromstring(string, fmt, resolution=DATETIME)

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                )

class CalendarDateTimeMicro(_CalendarDate):
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0):
        super().__init__(year, month, day, hour, minute, second, microsecond, resolution=DATETIMEMS)

    @staticmethod
    def now():
        """
        Return the current time as a calendar date with *datetimems* resolution.
        """
        return _CalendarDate.fromtimestamp(time.time(), DATETIMEMS)

    @staticmethod
    def fromtimestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp, timezone.utc)

        result = CalendarDate.__new__(CalendarDate)
        result._pydate = dt
        result._resolution = DATETIMEMS

        return result

    @classmethod
    def fromstring(cls, string, fmt):
        return super(CalendarDateTimeMicro, cls).fromstring(string, fmt, resolution=DATETIMEMICRO)

    def __repr__(self):
        return "{}.{}({}, {}, {}, {}, {}, {}, {})".format(
                type(self).__module__,
                type(self).__name__,
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.microsecond,
                )



# ======================================================================
# Parsing date
# ======================================================================
def parseisodate(datestring):
    """
    Parse a string formated as an ISO 8601 calendar date.
    """
    return CalendarDate.fromstring(datestring, "%Y-%m-%d")

def parseisodatetime(datestring):
    """
    Parse a string formated as an ISO 8601 calendar date.
    """
    return CalendarDateTime.fromstring(datestring, "%Y-%m-%d %H:%M:%S")

def parseisodatetime_ms(datestring):
    """
    Parse a string formated as an ISO 8601 calendar date.
    """
    return CalendarDateTimeMicro.fromstring(datestring, "%Y-%m-%d %H:%M:%S.%f")

def parsetimestamp_d(datestring):
    """
    Parse a string encoding a calendar date as a number of seconds since Unix Epoch.
    """
    return CalendarDate.fromtimestamp(float(datestring))

def parsetimestamp_s(datestring):
    """
    Parse a string encoding a calendar date as a number of seconds since Unix Epoch.
    """
    return CalendarDateTime.fromtimestamp(float(datestring))

def parsetimestamp_ms(datestring):
    """
    Parse a string encoding a calendar date as a number of milliseconds since Unix Epoch.
    """
    return CalendarDateTimeMicro.fromtimestamp(float(datestring)/1000)
