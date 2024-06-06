import unittest

from fin.seq.fc.window import naive_window, aggregate_over, cumulate

from tests.fin.seq.fc import utilities

# ======================================================================
# Window functions
# ======================================================================
class TestWindow(unittest.TestCase):
    def test_one_column(self):
        col = utilities.apply(self,
            naive_window(sum, 2),
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        )

        self.assertSequenceEqual(col.py_values, [ None, 21, 23, 25, 27, 29, 31, 33, 35, 37 ])

import fin.seq.ag.core as ag
from fin.seq.serie import Serie
from fin.seq.column import Column
class TestAggregateOver(unittest.TestCase):
    """ Tests for the `aggregate function` -> `window function` bridge.
    """
    def test_one(self):
        XX = None
        test_cases = (
            "#0",
            [10, 11, 12, 13, 14],
            ag.sum, 3,
            [XX, XX, 33, 36, 39],
        )

        while test_cases:
            desc, seq, fct, n, expected, *test_cases = test_cases
            col = Column.from_sequence(seq)
            ser = Serie.create(col)
            with self.subTest(desc=desc):
                actual = aggregate_over(fct, n)(ser, col)
                self.assertSequenceEqual(actual, expected)

import fin.seq.ag.core as ag
from fin.seq.serie import Serie
from fin.seq.column import Column
class TestCumulate(unittest.TestCase):
    def test_one(self):
        XX = None
        test_cases = (
            "#0, cumulative sum",
            [10, 11, 12, 13, 14],
            ag.sum, 0,
            [10, 21, 33, 46, 60],

            "#0, cumulative sum with cap",
            [10, 11, 12, 13, 14],
            ag.sum, 3,
            [10, 21, 33, 36, 39],
        )

        while test_cases:
            desc, seq, fct, n, expected, *test_cases = test_cases
            col = Column.from_sequence(seq)
            ser = Serie.create(col)
            with self.subTest(desc=desc):
                actual = cumulate(fct, n)(ser, col)
                self.assertSequenceEqual(actual, expected)

