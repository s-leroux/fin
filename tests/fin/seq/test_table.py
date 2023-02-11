import unittest

from fin.seq import table
from fin.seq import algo

class TestTable(unittest.TestCase):
    def test_constructor(self):
        t = table.Table(0)

        self.assertEqual(t.rows(), 0)
        self.assertEqual(t.columns(), 0)

    def test_add_column_from_iterator(self):
        FROM=1
        TO=100
        t = table.Table(TO-FROM)

        t.add_column("X", range(FROM, TO))

        self.assertEqual(t.rows(), TO-FROM)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t._data[0], range(FROM, TO))

    def test_add_column_from_value(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", VALUE)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertEqual(t._data[0], [VALUE]*LEN)

    def test_add_column_from_function_zero_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", lambda n: [VALUE]*n)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertEqual(t._data[0], [VALUE]*LEN)

    def test_add_column_from_function_one_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", range(LEN))
        t.add_column("Y", lambda n, xs: [x+1 for x in xs], "X")

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 2)
        self.assertEqual(t._data[1], [x+1 for x in range(LEN)])

    def test_add_column_from_algo(self):
        LEN=10
        A=list(range(200, 200+LEN))
        B=list(range(300, 300+LEN))

        t = table.Table(LEN)
        t.add_column("A", A)
        t.add_column("B", B)
        t.add_column("C", algo.by_row(lambda a, b: a+b), "A", "B")
        self.assertEqual(t._data[2], list(range(500, 500+2*LEN, 2)))

    def test_naive_window(self):
        LEN=10
        A=list(range(10, 10+LEN))

        t = table.Table(LEN)
        t.add_column("A", A)
        t.add_column("B", algo.naive_window(sum, 2), "A")
        self.assertEqual(t._data[1], [None, 21, 23, 25, 27, 29, 31, 33, 35, 37])

    def test_get_column(self):
        LEN=5
        A=[1]*LEN
        B=[2]*LEN
        C=[3]*LEN
        t = table.Table(LEN)

        t.add_column("A", A)
        t.add_column("B", B)
        t.add_column("C", C)

        self.assertEqual(t.get_column(0)._column, A)
        self.assertEqual(t.get_column(1)._column, B)
        self.assertEqual(t.get_column(2)._column, C)

        self.assertEqual(t.get_column("A")._column, A)
        self.assertEqual(t.get_column("B")._column, B)
        self.assertEqual(t.get_column("C")._column, C)

    def test_eval(self):
        LEN=99
        VALUE=123

        t = table.Table(LEN)

        t.add_column("X", VALUE)
        result = t.eval(lambda n, xs:sum(xs), "X")

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertEqual(result, VALUE*LEN)

    def test_bad_col_length(self):
        t = table.Table(99)

        with self.assertRaises(table.InvalidError):
            t.add_column("X", [0.0]*100)

        with self.assertRaises(table.InvalidError):
            t.add_column("X", [0.0]*98)

class TestColumnRef(unittest.TestCase):
    def test_add(self):
        FROM = 1
        TO = 101
        N = 2
        t = table.Table(TO-FROM)

        t.add_column("X", range(FROM, TO))
        col = t.get_column(0)

        self.assertEqual(col+N, list(range(FROM+N, TO+N)))

class TestCSV(unittest.TestCase):
    def test_load(self):
        t = table.table_from_csv("tests/_fixtures/bd.csv", format="dn-n")

        self.assertEqual(t.rows(), 284)
        self.assertEqual(t.columns(), 3)

        time = t.get_column("time")
        self.assertEqual(time[0], "2022-01-03")
        self.assertEqual(time[-1], "2023-02-07")

        quote = t.get_column("BOURSE DIRECT")
        self.assertEqual(quote[0], 2.73)
        self.assertEqual(quote[-1], 3.49)
