import unittest

from fin.seq.smachine import py_evaluate
from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq import fc

class TestSMachineCore(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(Column.from_constant(3, i) for i in range(7))
        self.serie = Serie.create(
                Column.from_sequence("ABC"),
                *self.cols,
                )

    def test_eval(self):
        cols = self.cols

        testcases = (
                "#1.00",
                cols[1],
                (
                    1,
                ),
                "#1.01",
                ( fc.sub, cols[1], cols[2] ),
                (
                    -1,
                ),
                "#1.02",
                ( fc.add, cols[1], cols[2], ( fc.sub, cols[3], cols[4] ) ),
                (
                    2,
                ),
                "#1.03",
                ( fc.add, cols[1], cols[2], fc.sub, cols[3], cols[4] ),
                (
                    2,
                ),
                "#1.04",
                ( fc.add, cols[1], cols[2], ( fc.sub, cols[3], cols[4] ), cols[5] ),
                (
                    7,
                ),
                "#1.05",
                ( fc.add, ( fc.sub, cols[1], cols[2] ), ( fc.sub, cols[3], cols[4] ) ),
                (
                    -2,
                ),
                "#2.00",
                ( cols[1], cols[2] ),
                (
                    1, 2
                ),
                "#2.01",
                ( ( fc.add, cols[1], cols[2] ), ( fc.sub, cols[3], cols[4] ) ),
                (
                    3, -1
                ),
                "#3.00",
                ( cols[1], cols[2], cols[3] ),
                (
                    1, 2, 3
                ),
                "#3.01",
                (
                    ( fc.add, cols[3], cols[4] ),
                    ( fc.sub, cols[1], cols[2] ),
                    ( fc.add, cols[5], cols[6], cols[4] ),
                ),
                (
                    7, -1, 15
                ),
            )

        while testcases:
            desc, expr, expected, *testcases = testcases
            with self.subTest(desc=desc):
                res = py_evaluate(self.serie, expr)

                self.assertIsInstance(res, tuple)
                self.assertEqual(len(res), len(expected))
                for col, exp in zip(res, expected):
                    self.assertIsInstance(col, Column)
                    self.assertEqual(col, Column.from_constant(3, exp))

class TestSMachineFeat(unittest.TestCase):
    def test_get_by_name(self):
        T = Column.from_sequence("ABCDE", name="T"),
        X = Column.from_sequence(range(10,15), name="X")
        ser = Serie.create( T, X, )
        res = py_evaluate(ser, "X")
        self.assertSequenceEqual(res, (X,))

    def test_getitem(self):
        T = Column.from_sequence("ABCDE", name="T"),
        X = Column.from_sequence(range(10,15), name="X")
        Y = Column.from_sequence(range(20,25), name="Y")
        serX = Serie.create( T, X, )
        serY = Serie.create( T, Y, )
        res = py_evaluate(serX, serY["Y"])
        self.assertSequenceEqual(res, (Y,))

    def test_get_and_rename(self):
        T = Column.from_sequence("ABCDE", name="T"),
        X = Column.from_sequence(range(10,15), name="X")
        ser = Serie.create( T, X, )
        res = py_evaluate(ser, (fc.named("Y"), fc.get("X")))
        self.assertSequenceEqual(res, (X,))
        self.assertEqual(res[0].name, "Y")


