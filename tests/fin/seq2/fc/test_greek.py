import unittest

from fin.seq2.fc import greek

from tests.fin.seq2.fc import utilities

# ======================================================================
# Greek
# ======================================================================
class TestDelta(unittest.TestCase):
    def test_delta(self):
        LEN=10
        col = [*range(LEN)]

        expected = [None] + [1]*(LEN-1)
        actual = utilities.apply(self, greek.delta(), col)

        self.assertSequenceEqual(actual.py_values, expected)

    def test_delta_with_none(self):
        LEN=10
        IDX=5
        col = [*range(LEN)]
        col[IDX] = None

        expected = [None] + [1]*(LEN-1)
        expected[IDX] = None
        expected[IDX+1] = None
        actual = utilities.apply(self, greek.delta(), col)

        self.assertSequenceEqual(actual.py_values, expected)

class TestBeta(unittest.TestCase):
    def test_beta(self):
        LEN = 100
        WINDOW = 10
        COL_X = COL_Y = [*range(LEN)]
        EXPECTED = [None]*(WINDOW-1) + [1.0]*(LEN-WINDOW+1)

        actual = utilities.apply(self, greek.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual.py_values, EXPECTED)

    def test_beta_x10(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [x*10 for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [10.0]*(LEN-WINDOW+1)

        actual = utilities.apply(self, greek.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual.py_values, EXPECTED)

    def test_beta_neg(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [-x for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [-1.0]*(LEN-WINDOW+1)

        actual = utilities.apply(self, greek.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual.py_values, EXPECTED)

