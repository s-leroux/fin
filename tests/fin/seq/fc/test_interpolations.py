import unittest

from fin.seq import column
from fin.seq.fc import interpolations

from testing import assertions
from tests.fin.seq.fc import utilities

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
                        actual = utilities.apply(self, interpolations.line(a,b), X, Y)
                        self.assertFloatSequenceEqual(
                                actual,
                                EXPECTED,
                                )

