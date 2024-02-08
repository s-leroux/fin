import unittest
import time
import datetime

from fin.datetime import *
import builtins

# ======================================================================
# Calendar date delta
# ======================================================================
class TestCalendarDateDelta(unittest.TestCase):
    """
    Test suite for CalendarDateDelta, CalendarDateTimeDelta and CalendarDateTimeMicroDelta.
    """
    def test_init(self):
        """
        It should store the delta years, delta months and delta days properties.
        """
        date = CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, 5)
        self.assertEqual(date._months, 1)
        self.assertEqual(date._weeks, 3)
        self.assertEqual(date._days, 2)

    def test_neg(self):
        """
        It should support the unary minus operator
        """
        date = -CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, -5)
        self.assertEqual(date._months, -1)
        self.assertEqual(date._weeks, -3)
        self.assertEqual(date._days, -2)

    def test_pos(self):
        """
        It should support the unary plus operator
        """
        date = +CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, 5)
        self.assertEqual(date._months, 1)
        self.assertEqual(date._weeks, 3)
        self.assertEqual(date._days, 2)

    def test_ac_calendar_date_delta(self):
        use_cases = (
                CalendarDateDelta(years=5, months=1, weeks=3, days=2),
                dict(years=5, months=1, weeks=3, days=2),
                )
        for use_case in use_cases:
            with self.subTest(use_case=use_case):
                date = asCalendarDateDelta(use_case)
                self.assertEqual(date._years, 5)
                self.assertEqual(date._months, 1)
                self.assertEqual(date._weeks, 3)
                self.assertEqual(date._days, 2)

    def test_fromkeywords(self):
        """
        It should initialize from keyword arguments.
        Sub-precision properties are set to zero.
        """
        timestamp = 1707314518.2307596
        testcases=(
            CalendarDateDelta,
            dict(years=4, months=2, weeks=3, days=1),
            (4, 2, 3, 1, 0, 0, 0, 0),

            CalendarDateTimeDelta,
            dict(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7),
            (4, 2, 3, 1, 5, 6, 7, 0),

            CalendarDateTimeMicroDelta,
            dict(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7, microseconds=123456),
            (4, 2, 3, 1, 5, 6, 7, 123456),
        )

        while testcases:
            cls, kwargs, expected, *testcases = testcases
            with self.subTest(cls=cls):
                delta = cls(**kwargs)
                actual = (delta._years, delta._months, delta._weeks, delta._days, delta._hours, delta._minutes, delta._seconds, delta._microseconds)
                self.assertSequenceEqual(actual, expected)

    def test_eq(self):
        """
        Equality.
        """
        testcases=(
            CalendarDateDelta(years=4, months=2, weeks=3, days=1),
            CalendarDateDelta(years=4, months=2, weeks=3, days=1),
            CalendarDateDelta(years=3, months=2, weeks=3, days=1),

            # A week is seven days
            CalendarDateDelta(years=4, months=2, weeks=3, days=1),
            CalendarDateDelta(years=4, months=2, weeks=1, days=15),
            CalendarDateDelta(years=3, months=2, weeks=3, days=1),

            CalendarDateTimeDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7),
            CalendarDateTimeDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7),
            CalendarDateTimeDelta(years=4, months=2, weeks=3, days=1, hours=4, minutes=6, seconds=7),

            CalendarDateTimeMicroDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7, microseconds=123456),
            CalendarDateTimeMicroDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7, microseconds=123456),
            CalendarDateTimeMicroDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7, microseconds=1235),
        )

        while testcases:
            a, b, c, *testcases = testcases
            with self.subTest(a=a, b=b, c=c):
                self.assertTrue(a==a)
                self.assertTrue(a==b)
                self.assertTrue(a!=c)

    def test_arithmetic(self):
        """
        Arithmetic operations on CalendarDateDelta.
        """
        testcases=(
            CalendarDateDelta(years=4, months=2, weeks=3, days=1),
            CalendarDateDelta(years=-4, months=-2, weeks=-3, days=-1),

            CalendarDateTimeDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7),
            CalendarDateTimeDelta(years=-4, months=-2, weeks=-3, days=-1, hours=-5, minutes=-6, seconds=-7),

            CalendarDateTimeMicroDelta(years=4, months=2, weeks=3, days=1, hours=5, minutes=6, seconds=7, microseconds=123456),
            CalendarDateTimeMicroDelta(years=-4, months=-2, weeks=-3, days=-1, hours=-5, minutes=-6, seconds=-7, microseconds=-123456),
        )

        while testcases:
            a, b, *testcases = testcases
            with self.subTest(a=a, b=b):
                self.assertTrue(a==+a)
                self.assertTrue(b==+b)
                self.assertTrue(a==-b)
                self.assertTrue(b==-a)

# ======================================================================
# Calendar dates
# ======================================================================
TM_TIMESTAMP = 1707314518.230759  # 2024-02-07T14:01:58,230759000+00:00
                                  # date -d "@$TIMESTAMP" -u -Ins
# date -d "@TM_$TIMESTAMP" -u +"%Y-%m-%d %H:%M:%S.%N %z"
TM_TIMESTRING = "2024-02-07 14:01:58.230759000 +0000"
TM_DATE, TM_TIME, TM_OFFSET = TM_TIMESTRING.split()
TM_TIME, TM_MICRO = TM_TIME.split(".")
TM_YEAR=int(TM_DATE[0:4])
TM_MONTH=int(TM_DATE[5:7])
TM_DAY=int(TM_DATE[9:11])
TM_MICRO = TM_MICRO[:-3] # We only have microsecond precision here

class TestCalendarDate(unittest.TestCase):
    """
    Test suite for CalendarDate, CalendarDateTime and CalendarDateTimeMicro.
    """
    def test_init(self):
        """
        It should provides the year, month and day properties.
        """
        date = CalendarDate(2012, 11, 5)
        self.assertEqual(date.year, 2012)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.day, 5)

    def test_parse_iso_date_1(self):
        """
        It should parse ISO 8601 dates according to the YYYY-MM-DD format.
        """
        date = parseisodate("2023-01-21")
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 21)

    def test_parse_timestamp(self):
        """
        It should parse dates expressed as a number of seconds since Unix Epoch.
        """
        date = parsetimestamp(f"{TM_TIMESTAMP}", "DATE")
        self.assertEqual(str(date), f"{TM_DATE}")

    def test_parse_timestamp_ms(self):
        """
        It should parse dates expressed as a number of milliseconds since Unix Epoch.
        """
        date = parsetimestamp_ms(f"{TM_TIMESTAMP*1000}")
        self.assertEqual(str(date), f"{TM_DATE}T{TM_TIME}.{TM_MICRO}")

    def test_init_from_timestamp(self):
        """
        The factory method should create a CalendarDate object from a timestamp.
        """
        ts = 1680121175
        st = time.localtime(ts)
        cd = CalendarDate.fromtimestamp(ts)

        self.assertEqual(cd.year, 2023)
        self.assertEqual(cd.month, 3)
        self.assertEqual(cd.day, 29)

    def test_today(self):
        """
        The factory method should create a CalendarDate for today.
        """
        DAYS=24*60*60
        before = time.time()//DAYS*DAYS
        cd = CalendarDate.today()
        after = time.time()//DAYS*DAYS

        self.assertGreaterEqual(cd.timestamp, before)
        self.assertLessEqual(cd.timestamp, after)
        self.assertEqual(cd.timestamp%DAYS, 0)

    def test_timestamp(self):
        """
        The timestamp property should return the number of seconds since 1970-01-01.
        """
        ts = 1680048000
        cd = parseisodate("2023-03-29")

        self.assertEqual(cd.timestamp, ts)


    def test_str(self):
        """
        __str__ should produce string following the  YYYY-MM-DD format.
        """
        datestring = "1999-06-30"
        date = parseisodate(datestring)
        self.assertEqual(str(date), datestring)

    def test_fromtimestamp(self):
        """
        It should set the required properties when converting from timestamp.
        Sub-precision properties are set to zero.
        """
        timestamp = 1707314518.2307596
        testcases=(
            CalendarDate, (2024, 2, 7, 0, 0, 0, 0),
            CalendarDateTime, (2024, 2, 7, 14, 1, 58, 0),
            CalendarDateTimeMicro, (2024, 2, 7, 14, 1, 58, 230760)
        )

        while testcases:
            cls, expected, *testcases = testcases
            with self.subTest(cls=cls):
                date = cls.fromtimestamp(timestamp)
                actual = (date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond)
                self.assertSequenceEqual(actual, expected)

    def test_str(self):
        """
        It should format the date as a string using the right format.
        """
        timestamp = TM_TIMESTAMP
        testcases=(
            CalendarDate, f"{TM_DATE}",
            CalendarDateTime, f"{TM_DATE}T{TM_TIME}",
            CalendarDateTimeMicro, f"{TM_DATE}T{TM_TIME}.{TM_MICRO}",
        )

        while testcases:
            cls, expected, *testcases = testcases
            with self.subTest(cls=cls):
                date = cls.fromtimestamp(timestamp)
                actual = str(date)
                self.assertEqual(actual, expected)

    def test_timestamp_and_back(self):
        """
        It should convert to timestamp with adequate precision.
        """
        DAY=24*60*60
        digits = 4 # significant digits since this is subject to rounding errors
        timestamp = TM_TIMESTAMP
        testcases=(
            CalendarDate, TM_TIMESTAMP//DAY*DAY,
            CalendarDateTime, round(TM_TIMESTAMP),
            CalendarDateTimeMicro, TM_TIMESTAMP,
        )

        while testcases:
            cls, expected, *testcases = testcases
            with self.subTest(cls=cls):
                date = cls.fromtimestamp(timestamp)
                actual = date.timestamp
                self.assertEqual(round(actual,digits), round(expected,digits))

# ======================================================================
# Calendar date math
# ======================================================================
class TestCalendarDateMath(unittest.TestCase):
    def test_add(self):
        """
        We may add a CalendarDateDelta to a CalendarDate
        """
        test_cases = (
                    "2012-11-17", "2011-11-17", dict(years=-1), # Basic use case
                    "2020-03-01", "2020-02-29", dict(days=-1),  # Month changing
                    "2020-12-12", "2021-01-02", dict(weeks=3),  # Year changing
                    "2020-11-01", "2021-02-01", dict(months=3), # Year changing
                    "2020-03-01", "2020-01-31", dict(months=-1, days=-1), # Check that months are subtracted first
                    "2008-12-01", "2009-12-01", dict(years=1),  # Known bug in some versions
                    "2008-12-01", "2007-12-01", dict(years=-1),  # Known bug in some versions
                    "2008-12-01", "2010-12-01", dict(months=24),  # Known bug in some versions
                    "2008-12-01", "2006-12-01", dict(months=-24),  # Known bug in some versions
                )

        for date, expected, delta in zip(*[iter(test_cases)]*3):
            with self.subTest(date=date, delta=delta):
                date = parseisodate(date)
                delta = CalendarDateDelta(**delta)
                actual = date + delta

                msg = "{}+{} = {}".format(date, delta, expected)
                self.assertEqual(str(actual), expected, msg)

class TestCalendarDateIterator(unittest.TestCase):
    def test_iterate_by_inline_arg(self):
        date = parseisodate("2023-03-27")
        interval = CalendarDateDelta(days=1)

        a = [*date.iter_by(interval, n=3)]
        b = [*date.iter_by(days=1, n=3)]

        self.assertEqual(a,b)

    def test_iterate_by(self):
        date = parseisodate("2023-03-27")
        interval = CalendarDateDelta(days=1)

        expected = (
                "2023-03-28",
                "2023-03-29",
                "2023-03-30",
                "2023-03-31",
                "2023-04-01",
                "2023-04-02",
                )
        actual = tuple(date.iter_by(interval, n=len(expected)))
        self.assertEqual(tuple(map(str,actual)), expected)
