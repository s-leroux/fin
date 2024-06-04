import unittest

from fin.seq.column import Column
from fin.seq.ag import core

class TestCoreAggregate(unittest.TestCase):
    def test_sum(self):
        test_cases = (
            #
            # First
            #
            "#1.0 First, all data",
            "abcdef",
            core.First, 0, 6,
            "a",

            "#1.1 First, one data",
            "abcdef",
            core.First, 3, 4,
            "d",

#            "#1.2 First, no data",
#            "abcdef",
#            core.First, 4, 4,
#            None,

            "#1.3 First, range",
            "abcdef",
            core.First, 1, 4,
            "b",

            #
            # Count
            #
            "#1.0 Count, all data",
            "abcdef",
            core.Count, 0, 6,
            6,

            "#1.1 Count, one data",
            "abcdef",
            core.Count, 3, 4,
            1,

            "#1.2 Count, no data",
            "abcdef",
            core.Count, 4, 4,
            0,

            "#1.3 Count, range",
            "abcdef",
            core.Count, 1, 4,
            3,

            #
            # Sum
            #
            "#1.0 Sum, all data",
            [0,1,2,3,4,5,6,7],
            core.Sum, 0, 8,
            28,

            "#1.1 Sum, one data",
            [0,1,2,3,4,5,6,7],
            core.Sum, 3, 4,
            3,

            "#1.2 Sum, no data",
            [0,1,2,3,4,5,6,7],
            core.Sum, 4, 4,
            0,

            "#1.3 Sum, range",
            [0,1,2,3,4,5,6,7],
            core.Sum, 1, 4,
            6,

            #
            # Avg
            #
            "#1.0 Avg, all data",
            [0,1,2,3,4,5,6,7],
            core.Avg, 0, 8,
            28/8,

            "#1.1 Avg, one data",
            [0,1,2,3,4,5,6,7],
            core.Avg, 3, 4,
            3,

#            "#1.2 Avg, no data",
#            [0,1,2,3,4,5,6,7],
#            core.Avg, 4, 4,
#            float("NaN"),

            "#1.3 Avg, range",
            [0,1,2,3,4,5,6,7],
            core.Avg, 1, 4,
            6/3,

        )

        while test_cases:
            desc, seq, fct_factory, begin, end, expected, *test_cases = test_cases

            col = Column.from_sequence(seq)
            with self.subTest(desc=desc):
                fct = fct_factory()
                self.assertEqual(fct(col, begin, end), expected)
