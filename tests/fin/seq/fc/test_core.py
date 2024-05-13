import unittest

from fin.seq import column
from fin.seq.fc import core

from tests.fin.seq.fc import utilities

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

    def test_range(self):
        testcases = (
            (5,),
            (1,5),
            (1,5,2),
        )

        for testcase in testcases:
            with self.subTest(testcase=testcase):
                col = utilities.apply(self, core.range(*testcase), rowcount=len(range(*testcase)))
                self.assertSequenceEqual(col.py_values, range(*testcase))

    def test_get(self):
        serie = dict(X=object())

        fct = core.get("X")
        obj = fct(serie)

        self.assertIs(obj, serie["X"])

    def test_shift(self):
        col = column.Column.from_sequence((1,2,3,4,5))
        fct = core.shift(3)
        col = fct(None, col)

        self.assertSequenceEqual(col.py_values, (4,5,None,None,None))

    def test_rownum(self):
        LEN = 10
        serie = type("SerieMock",(),dict(rowcount=LEN))()
        col = core.rownum(serie)

        self.assertSequenceEqual(tuple(col), range(LEN))

    def test_coalesce(self):
        XX = None
        cols = (
                ( 10, XX, XX, XX, XX, 15, ),
                ( XX, 21, XX, XX, XX, 25, ),
                ( 30, 31, 32, XX, XX, XX, ),
                ( 40, 41, 42, 43, XX, 45, ),
            )
        expected = \
                ( 10, 21, 32, 43, XX, 15, )

        res = utilities.apply(self, core.coalesce, *[column.Column.from_sequence(col) for col in cols])
        self.assertIsInstance(res, column.Column)
        self.assertSequenceEqual(res, expected)

class TestCoreFunctions2(unittest.TestCase):
    def setUp(self):
        master = column.Column.from_sequence(range(-10, 10))
        self.cols = (
                ("py", column.Column.from_sequence(master.py_values, name="X")),
                ("t", column.Column.from_ternary_mv(master.t_values, name="X", type="t")),
                ("f", column.Column.from_float_mv(master.f_values, name="X", type="n")),
            )

    def test_named(self):
        old_name = "X"
        new_name = "Y"
        fct = core.named(new_name)
        for desc, col in self.cols:
            with self.subTest(desc=desc):
                self.assertEqual(col.name, old_name)
                col = fct(None, col)
                self.assertEqual(col.name, new_name)

