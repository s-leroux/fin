import unittest

from fin.seq2 import column
from fin.seq2.fc import core

# ======================================================================
# Mock series
# ======================================================================
class SerieMock:
    def __init__(self, **kwargs):
        self._properties = kwargs

    def __getattr__(self, name):
        # Emulate read-only properties
        return self._properties[name]

# ======================================================================
# Mock series
# ======================================================================
class TestCoreFunctions(unittest.TestCase):
    def call(self, fct, expected, **kwargs):
        serie = SerieMock(**kwargs)

        col = fct(serie)
        
        self.assertIsInstance(col, column.Column)
        self.assertEqual(col.py_values, expected)

    def test_constant(self):
        n = 11
        rowcount = 8
        self.call(core.constant(n), (n,)*rowcount, rowcount = rowcount)

    def test_sequence(self):
        testcases = (
            tuple(range(100)),
            list(range(100)),
            "ABCDEF",
                )

        for seq in testcases:
            with self.subTest(seq=seq):
                self.call(core.sequence(seq), tuple(seq))
        self.call(core.sequence(seq), tuple(seq))

    def test_named(self):
        serie = SerieMock()
        old_name = "X"
        new_name = "Y"
        col = column.Column.from_sequence("ABCDEF", name=old_name)
        fct = core.named(new_name)
        col = fct(serie, col)

        self.assertEqual(col.name, new_name)

