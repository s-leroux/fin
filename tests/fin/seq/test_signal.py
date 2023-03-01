import unittest

from fin.seq import signal
from fin.seq import table

# ======================================================================
# Utilities
# ======================================================================
def call_signal(s, rowcount, d):
    f, *colnames = s
    args = [d[colname] for colname in colnames]
    return f(rowcount, *args)

# ======================================================================
# Signals
# ======================================================================
class TestAbove(unittest.TestCase):
    def test_data(self):
        LIMIT = 5.0
        LEN = 10
        a = [*range(LEN)]
        b = [LIMIT]*LEN

        expected = [x > y for x,y in zip(a,b)]
        actual = call_signal(signal.above("X","Y"), LEN, dict(X=a, Y=b))
        self.assertSequenceEqual(actual, expected)

class TestBelow(unittest.TestCase):
    def test_data(self):
        LIMIT = 5.0
        LEN = 10
        a = [*range(LEN)]
        b = [LIMIT]*LEN

        expected = [x < y for x,y in zip(a,b)]
        actual = call_signal(signal.below("X","Y"), LEN, dict(X=a, Y=b))
        self.assertSequenceEqual(actual, expected)

class TestAlmostEqual(unittest.TestCase):
    def test_data(self):
        LIMIT = 5.0
        LEN = 10
        a = [*range(LEN)]
        b = [LIMIT]*LEN
        delta = [1]*LEN

        expected = [-delta <= x-y <= delta for x,y,delta in zip(a,b,delta)]
        actual = call_signal(signal.almost_equal("X","Y", "DELTA"), LEN, dict(X=a, Y=b, DELTA=delta))
        self.assertSequenceEqual(actual, expected)

class TestIncrease(unittest.TestCase):
    def test_data(self):
        THRESHOLD = 1.0
        LEN = 10
        a = [*range(0, LEN, 1)] + [*range(LEN, 0, -1)]
        b = [THRESHOLD]*LEN
        rows = [*zip(a,b)]

        expected = [n > 0 and rows[n][0]-rows[n-1][0] > rows[n][1] for n in range(len(rows))]
        actual = call_signal(signal.increase("X","Y"), LEN, dict(X=a, Y=b))
        self.assertSequenceEqual([x or False for x in actual], expected)

# ======================================================================
# Algorithms
# ======================================================================
class TestPattern(unittest.TestCase):
    def test_pattern(self):
        LIMIT1 = 2.0
        LIMIT2 = 5.0
        LEN = 10
        A = [*range(0, LEN, 1)]

        t = table.table_from_dict(dict(
            A=A,
            ))

        expected = [i > 0 and A[i] > LIMIT1 and A[i-1] < LIMIT2 for i in range(LEN)]
        [actual] = t.reval(signal.pattern(
            signal.above("A", LIMIT1),
            signal.below("A", LIMIT2),
            ))
        self.assertSequenceEqual(actual, expected)


# ======================================================================
# Quantifiers
# ======================================================================
class TestAll(unittest.TestCase):
    def test_data(self):
        LIMIT = 5.0
        LEN = 10
        A = [*range(0, LEN, 1)]
        B = [*range(0, 2*LEN, 2)]

        t = table.table_from_dict(dict(
            A=A,
            B=B,
            ))

        expected = [a > 5 and b > 5 for a,b in zip(A,B)]
        [actual] = t.reval(signal.all(
                signal.above("A", LIMIT),
                signal.above("B", LIMIT),
            ))
        self.assertSequenceEqual(actual, expected)

class TestAny(unittest.TestCase):
    def test_data(self):
        LIMIT1 = 2.0
        LIMIT2 = 7.0
        LEN = 10
        A = [*range(0, LEN, 1)]

        t = table.table_from_dict(dict(
            A=A,
            ))

        expected = [a < LIMIT1 or a > LIMIT2 for a in A]
        [actual] = t.reval(signal.any(
                signal.below("A", LIMIT1),
                signal.above("A", LIMIT2),
            ))
        self.assertSequenceEqual(actual, expected)

