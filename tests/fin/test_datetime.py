import unittest
import time
import datetime

import fin.datetime
import builtins

# ======================================================================
# Calendar date delta
# ======================================================================
class TestCalendarDateDelta(unittest.TestCase):
    def test_init(self):
        """
        It should store the delta years, delta months and delta days properties.
        """
        date = fin.datetime.CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, 5)
        self.assertEqual(date._months, 1)
        self.assertEqual(date._weeks, 3)
        self.assertEqual(date._days, 2)

    def test_neg(self):
        """
        It should support the unary minus operator
        """
        date = -fin.datetime.CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, -5)
        self.assertEqual(date._months, -1)
        self.assertEqual(date._weeks, -3)
        self.assertEqual(date._days, -2)

    def test_pos(self):
        """
        It should support the unary plus operator
        """
        date = +fin.datetime.CalendarDateDelta(years=5, months=1, weeks=3, days=2)
        self.assertEqual(date._years, 5)
        self.assertEqual(date._months, 1)
        self.assertEqual(date._weeks, 3)
        self.assertEqual(date._days, 2)

    def test_ac_calendar_date_delta(self):
        use_cases = (
                fin.datetime.CalendarDateDelta(years=5, months=1, weeks=3, days=2),
                dict(years=5, months=1, weeks=3, days=2),
                )
        for use_case in use_cases:
            with self.subTest(use_case=use_case):
                date = fin.datetime.asCalendarDateDelta(use_case)
                self.assertEqual(date._years, 5)
                self.assertEqual(date._months, 1)
                self.assertEqual(date._weeks, 3)
                self.assertEqual(date._days, 2)

# ======================================================================
# Calendar dates
# ======================================================================
class TestCalendarDate(unittest.TestCase):
    def test_init(self):
        """
        It should provides the year, month and day properties.
        """
        date = fin.datetime.CalendarDate(2012, 11, 5)
        self.assertEqual(date.year, 2012)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.day, 5)

    def test_parse_iso_date_1(self):
        """
        It should parse ISO dates according to the YYYY-MM-DD format.
        """
        date = fin.datetime.parseisodate("2023-01-21")
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 21)

    def test_init_from_timestamp(self):
        """
        The factory method should create a CalendarDate object from a timestamp.
        """
        ts = 1680121175
        st = time.localtime(ts)
        cd = fin.datetime.CalendarDate.fromtimestamp(ts)

        self.assertEqual(cd.year, 2023)
        self.assertEqual(cd.month, 3)
        self.assertEqual(cd.day, 29)

    def test_today(self):
        """
        The factory method should create a CalendarDate for today.
        """
        DAYS=24*60*60
        now = time.time()
        cd = fin.datetime.CalendarDate.today()

        self.assertGreaterEqual(cd.timestamp//DAYS, now//DAYS)
        self.assertLessEqual(cd.timestamp, now+1)

    def test_timestamp(self):
        """
        The timestamp property should return the number of seconds since 1970-01-01.
        """
        ts = 1680048000
        cd = fin.datetime.CalendarDate.fromisoformat("2023-03-29")

        self.assertEqual(cd.timestamp, ts)


    def test_str(self):
        """
        __str__ should produce string following the  YYYY-MM-DD format.
        """
        datestring = "1999-06-30"
        date = fin.datetime.parseisodate(datestring)
        self.assertEqual(str(date), datestring)

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
                date = fin.datetime.parseisodate(date)
                delta = fin.datetime.CalendarDateDelta(**delta)
                actual = date + delta

                msg = "{}+{} = {}".format(date, delta, expected)
                self.assertEqual(str(actual), expected, msg)

class TestCalendarDateIterator(unittest.TestCase):
    def test_iterate_by_inline_arg(self):
        date = fin.datetime.parseisodate("2023-03-27")
        interval = fin.datetime.CalendarDateDelta(days=1)

        a = [*date.iter_by(interval, n=3)]
        b = [*date.iter_by(days=1, n=3)]

        self.assertEqual(a,b)

    def test_iterate_by(self):
        date = fin.datetime.parseisodate("2023-03-27")
        interval = fin.datetime.CalendarDateDelta(days=1)

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
