import unittest

from fin.seq2 import column
from fin.seq2.fc import core

from tests.fin.seq2.fc import utilities

# ======================================================================
# Core functions
# ======================================================================
class TestCoreFunctions(unittest.TestCase):
    def test_constant(self):
        n = 11
        rowcount = 8
        col = utilities.apply(self, core.constant(n), rowcount=rowcount)
        self.assertSequenceEqual(col.py_values, (11,)*rowcount)

    def test_sequence(self):
        testcases = (
            tuple(range(100)),
            list(range(100)),
            "ABCDEF",
                )

        for seq in testcases:
            with self.subTest(seq=seq):
                col = utilities.apply(self, core.sequence(seq), rowcount=len(seq))
                self.assertSequenceEqual(col.py_values, seq)

    def test_get(self):
        serie = dict(X=object())

        fct = core.get("X")
        obj = fct(serie)

        self.assertIs(obj, serie["X"])

    def test_named(self):
        old_name = "X"
        new_name = "Y"
        col = column.Column.from_sequence("ABCDEF", name=old_name)
        fct = core.named(new_name)
        col = fct(None, col)

        self.assertEqual(col.name, new_name)

    def test_shift(self):
        col = column.Column.from_sequence((1,2,3,4,5))
        fct = core.shift(3)
        col = fct(None, col)

        self.assertSequenceEqual(col.py_values, (4,5,None,None,None))
