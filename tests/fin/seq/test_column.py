import unittest

from fin.seq import table, column

# ======================================================================
# Columns
# ======================================================================
class TestColumn(unittest.TestCase):
    def test_eq(self):
        LEN=1
        t1 = table.Table(LEN)
        t1.add_column("A", 1)
        t1.add_column("B", 2)

        t2 = table.Table(LEN)
        t2.add_column("A", 1)
        t2.add_column("B", 1)

        # self equality (aka identity)
        self.assertEqual(t1["A"], t1["A"])
        self.assertEqual(t1["B"], t1["B"])
        self.assertEqual(t2["A"], t2["A"])
        self.assertEqual(t2["B"], t2["B"])

        # (in)equality
        self.assertEqual(t1["A"], t2["A"])
        self.assertNotEqual(t1["A"], t1["B"])
        self.assertNotEqual(t1["A"], t2["B"])

    def test_type(self):
        use_cases = (
                ( [1.0]*10, float),
                ( [1.0]*10 + [None], float),
                ( [None] + [1.0]*10 + [None], float),
                ( [1.0]*10 + ["X"], None),
                )

        for values, expected in use_cases:
            with self.subTest(values=values):
                column = table.Column("X", values)
                self.assertEqual(column.type(), expected)

    def test_slice(self):
        LEN=10
        column = table.Column("X", range(LEN))
        use_cases = (
                ( 0, LEN ),
                ( 0, LEN+1 ),
                ( 1, LEN ),
                ( 1, LEN // 2 + 1),
                )

        for use_case in use_cases:
            with self.subTest(use_case=use_case):
                start, end = use_case
                self.assertSequenceEqual(column.slice(start, end).values, column.values[start:end])

