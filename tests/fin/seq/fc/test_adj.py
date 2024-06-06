import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq.fc.adj import *

# ======================================================================
# Arithmetic operators
# ======================================================================
class TestAdjustQuote(unittest.TestCase):
    def setUp(self):
        cols = self.cols = tuple(zip(
                # op, hi, lo, cl, adj_cl
                ( 40, 60, 20, 40, 40 ),
                ( 40, 60, 20, 40, 20 ),
                ( 44, 64, 24, 44, 22 ),
                ( 88,128, 48, 88, 44 ),
            ))

        self.serie = Serie.create(
                Column.from_sequence(range(4), name="T"),
                *[ Column.from_sequence(col, name=n) for col,n in zip(cols, "ABCDE") ]
            )

    def test_adj(self):
        res = self.serie.select(
                "T",
                (adj, "A", "B", "C", "D", "E"),
            )

        rc = res.data
        self.assertEqual(len(rc), 4)
        self.assertSequenceEqual(rc[0].py_values, ( 40, 20, 22, 44 ) )
        self.assertSequenceEqual(rc[1].py_values, ( 60, 30, 32, 64 ) )
        self.assertSequenceEqual(rc[2].py_values, ( 20, 10, 12, 24 ) )
        self.assertSequenceEqual(rc[3].py_values, ( 40, 20, 22, 44 ) )

