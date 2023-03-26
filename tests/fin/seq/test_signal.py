import unittest

from fin.seq import signal, table, column

# ======================================================================
# Signals
# ======================================================================
class TestAbove(unittest.TestCase):
    def test_data(self):
        LEN = 10

        t = table.Table(LEN, columns=dict(
            A=column.ramp(),
            B=column.constant(5.0),
            ))

        expected = [x > y for x,y in zip(t["A"],t["B"])]
        [actual] = t.reval(signal.above(), "A","B")
        self.assertSequenceEqual(actual, expected)

class TestBelow(unittest.TestCase):
    def test_data(self):
        LEN = 10

        t = table.Table(LEN, columns=dict(
            A=column.ramp(),
            B=column.constant(5.0),
            ))

        expected = [x < y for x,y in zip(t["A"],t["B"])]
        [actual] = t.reval(signal.below(), "A","B")

class TestAlmostEqual(unittest.TestCase):
    def test_data(self):
        LEN = 10

        t = table.Table(LEN, columns=dict(
            A=column.ramp(),
            B=column.constant(5.0),
            DELTA=column.constant(1.0),
            ))

        expected = [-delta <= a-b <= delta for a,b,delta in zip(t["A"],t["B"],t["DELTA"])]
        [actual] = t.reval(signal.almost_equal(), "A","B", "DELTA")
        self.assertSequenceEqual(actual, expected)

class TestIncrease(unittest.TestCase):
    def test_data(self):
        LEN = 10
        A = [*range(LEN), *range(LEN, 0, -1)]
        t = table.Table(LEN*2, columns=dict(
            A=column.iterable(A),
            ))

        expected = [None] + [True]*LEN + [False]*(LEN-1)
        [actual] = t.reval(signal.increase(), "A")
        self.assertSequenceEqual(actual, expected)

# ======================================================================
# Algorithms
# ======================================================================
class TestPattern(unittest.TestCase):
    @unittest.skip
    def test_pattern(self):
        LEN = 10
        LIMIT1 = column.constant(2.0)
        LIMIT2 = column.constant(5.0)
        A = column.ramp()

        t = table.Table(LEN, columns=dict(
            A=A,
            LIMIT1=LIMIT1,
            LIMIT2=LIMIT2,
            ))

        expected = [a > l1 and a < l2 for a,l1,l2 in zip(t["A"], t["LIMIT1"], t["LIMIT2"])]
        # FIXME
        [actual] = t.reval(signal.pattern(
            signal.above("A", LIMIT1),
            signal.below("A", LIMIT2),
            ))
        self.assertSequenceEqual(actual, expected)

class TestWhen(unittest.TestCase):
    def test_when(self):
        LEN = 10

        t = table.Table(LEN,columns=dict(
            A = column.constant(2.0),
            B = column.constant(5.0),
            LIMIT = 5,
            T = column.ramp(),
            ))

        expected = [a if t > l else b for t,l,a,b in zip(t["T"],t["LIMIT"],t["A"],t["B"])]
        [actual] = t.reval(signal.when(), (signal.above(), "T", "LIMIT"), "A", "B")
        self.assertSequenceEqual(actual, expected)

# ======================================================================
# Quantifiers
# ======================================================================
class TestAll(unittest.TestCase):
    def test_data(self):
        LEN = 10

        t = table.Table(LEN, columns=dict(
            A=column.iterable([*range(0, LEN, 1)]),
            LIMIT1=column.constant(2.0),
            LIMIT2=column.constant(7.0),
            ))

        expected = [a > l1 and a < l2 for a,l1,l2 in zip(t["A"],t["LIMIT1"],t["LIMIT2"])]
        [actual] = t.reval(signal.all(
                (signal.above(),"A", "LIMIT1"),
                (signal.below(),"A", "LIMIT2"),
            ))
        self.assertSequenceEqual(actual, expected)

class TestAny(unittest.TestCase):
    def test_data(self):
        LEN = 10

        t = table.Table(LEN, columns=dict(
            A=column.iterable([*range(0, LEN, 1)]),
            LIMIT1=column.constant(2.0),
            LIMIT2=column.constant(7.0),
            ))

        expected = [a < l1 or a > l2 for a,l1,l2 in zip(t["A"],t["LIMIT1"],t["LIMIT2"])]
        [actual] = t.reval(signal.any(
                (signal.below(),"A", "LIMIT1"),
                (signal.above(),"A", "LIMIT2"),
            ))
        self.assertSequenceEqual(actual, expected)

