import unittest

from fin.datetime import parseisodate
from fin.seq2.column import Column
from fin.seq2.fc import calendars

from tests.fin.seq2.fc import utilities

# ======================================================================
# Calendar functions
# ======================================================================
DATE_COLUMN_A=Column.from_sequence(
    tuple(parseisodate("2008-08-15").iter_by(n=10,days=1)),
    name="DATE",
)
# One year later
DATE_COLUMN_B=Column.from_sequence(
    tuple(parseisodate("2009-08-15").iter_by(n=10,days=1)),
    name="DATE",
)

class TestCalendarFunctions(unittest.TestCase):
    def test_shift_date(self):
        res = utilities.apply(
                self,
                calendars.shift_date(dict(years=1)),
                DATE_COLUMN_A,
        )

        self.assertEqual(res, DATE_COLUMN_B)

