import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq.ag import stat
from fin.seq.fc.window import cumulate

class TestStatAggregate(unittest.TestCase):
    def test_stat_ag(self):
        XX = None
        test_cases = (
            #
            # Drawdown
            #
            "#1.0 Drawdown, monotically ascending",
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            stat.drawdown, 5,
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],

            "#1.1 Drawdown, monotically descending",
            [19, 18, 17, 16, 15, 14, 13, 12, 11, 10],
            stat.drawdown, 5,
            [ 0,  1,  2,  3,  4,  4,  4,  4,  4,  4],

            "#1.2 Drawdown, random order",
            [17, 12, 16, 11, 10, 19, 18, 14, 13, 15],
            stat.drawdown, 5,
            [ 0,  5,  1,  6,  7,  0,  1,  5,  6,  4],

            "#1.3 Drawdown, undefined data",
            [17, 12, 16, 11, XX, 19, 18, 14, 13, 15],
            stat.drawdown, 5,
            [ 0,  5,  1,  6, XX, XX, XX, XX, XX,  4],

            #
            # Maximun drawdown
            #
            "#1.0 Maximum Drawdown, monotically ascending",
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            stat.maximum_drawdown, 5,
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],

            "#1.1 Maximum Drawdown, monotically descending",
            [19, 18, 17, 16, 15, 14, 13, 12, 11, 10],
            stat.maximum_drawdown, 5,
            [ 0,  1,  2,  3,  4,  4,  4,  4,  4,  4],

            "#1.2 Maximum Drawdown, random order",
            [17, 12, 16, 11, 10, 19, 18, 14, 13, 15],
            stat.maximum_drawdown, 5,
            [ 0,  5,  5,  6,  7,  6,  6,  5,  6,  6],

            "#1.3 Maximum Drawdown, undefined data",
            [17, 12, 16, 11, XX, 19, 18, 14, 13, 15],
            stat.maximum_drawdown, 5,
            [ 0,  5,  5,  6, XX, XX, XX, XX, XX,  6],

        )

        while test_cases:
            desc, seq, fct, n, expected, *test_cases = test_cases

            idx = Column.from_sequence(range(len(seq)))
            col = Column.from_sequence(seq)
            ser = Serie.create(idx, col)
            with self.subTest(desc=desc):
                self.assertSequenceEqual(cumulate(fct, n)(ser, col), expected)
