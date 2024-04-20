import unittest

from fin.seq.column import Column
from fin.seq.coltypes import Ternary
from fin.seq.serie import Serie
from fin.seq.fc import logic

# ======================================================================
# Constants
# ======================================================================
T = True
F = False
N = None

# ======================================================================
# Logic operators
# ======================================================================
class TestArithmeticOperators(unittest.TestCase):
    def test_all(self):
        testcases = (
                (
                    "0-col truth table",
                    (T, T, T),
                ),
                (
                    "1-col truth table",
                    (T, F, N),
                    # -------------------------
                    (T, F, N),
                ),
                (
                    "2-cols truth table",
                    (T, F, T, T, N, F, N, N, F),
                    (T, T, F, N, T, F, F, N, N),
                    # -------------------------
                    (T, F, F, N, N, F, F, N, F),
                ),
                (
                    "3-cols truth table",
            (T, T, T, T, T, T, T, T, T, F, F, F, F, F, F, F, F, F, N, N, N, N, N, N, N, N, N),
            (T, T, T, F, F, F, N, N, N, T, T, T, F, F, F, N, N, N, T, T, T, F, F, F, N, N, N),
            (T, F, N, T, F, N, T, F, N, T, F, N, T, F, N, T, F, N, T, F, N, T, F, N, T, F, N),
                    # -------------------------
            (T, F, N, F, F, F, N, F, N, F, F, F, F, F, F, F, F, F, N, F, N, F, F, F, N, F, N),
                ),
            )

        for desc, *cols, expected in testcases:
            cols = [ Column.from_sequence(col, type=Ternary()) for col in cols ]
            with self.subTest(desc=desc):
                ser = Serie.create(Column.from_sequence(range(len(expected))))
                fct = logic.all
                res = fct(ser, *cols)

                self.assertIsInstance(res, Column)
                self.assertSequenceEqual(res, expected)

