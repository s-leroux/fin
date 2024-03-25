import unittest

from fin.seq2 import column
from fin.seq2.fc import interpolation

from testing import assertions
from tests.fin.seq2.mock import SerieMock

# ======================================================================
# Test utilities
# ======================================================================
def apply(self, fct, *cols, rowcount=None):
    if rowcount is None:
        rowcount = len(cols[0])

    serie = SerieMock(rowcount=rowcount)
    result = fct(serie, *cols)
    self.assertIsInstance(result, column.Column)

    return result

# ======================================================================
# Interpolation
# ======================================================================
class TestLine(unittest.TestCase, assertions.ExtraTests):
    def test_line(self):
        LEN = 10
        X = [*range(LEN)]
        Y = [x*10.0 for x in X]
        EXPECTED=Y.copy()
        for a in range(LEN):
            for b in range(LEN):
                if a != b:
                    with self.subTest(locals=locals()):
                        actual = apply(self, interpolation.line(a,b), X, Y)
                        self.assertSequenceTrue(
                                assertions.almostEqual(ndigits=8),
                                actual,
                                EXPECTED
                                )

