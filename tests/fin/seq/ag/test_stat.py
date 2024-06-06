import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq.ag import stat
from fin.seq.fc.window import aggregate_over

class TestStatAggregate(unittest.TestCase):
    def test_stat_ag(self):
        XX = None
        test_cases = (
            #
            # Maximun drawdown
            #
            "#1.0 Maximum Drawdown, monotically ascending",
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            stat.maximum_drawdown, 5,
            [XX, XX, XX, XX,  0,  0,  0,  0,  0,  0],

            "#1.1 Maximum Drawdown, monotically descending",
            [19, 18, 17, 16, 15, 14, 13, 12, 11, 10],
            stat.maximum_drawdown, 5,
            [XX, XX, XX, XX,  4,  4,  4,  4,  4,  4],

        )

        while test_cases:
            desc, seq, fct, n, expected, *test_cases = test_cases

            idx = Column.from_sequence(range(len(seq)))
            col = Column.from_sequence(seq)
            ser = Serie.create(idx, col)
            with self.subTest(desc=desc):
                self.assertSequenceEqual(aggregate_over(fct, n)(ser, col), expected)
