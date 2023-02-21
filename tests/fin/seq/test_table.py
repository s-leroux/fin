import unittest

from fin.seq import table
from fin.seq import algo

# ======================================================================
# Test table
# ======================================================================
class TestTable(unittest.TestCase):
    def test_constructor(self):
        t = table.Table(0)

        self.assertEqual(t.rows(), 0)
        self.assertEqual(t.columns(), 1+0)

    def test_add_column_from_iterator(self):
        FROM=1
        TO=100
        t = table.Table(TO-FROM)

        t.add_column("X", range(FROM, TO))

        self.assertEqual(t.rows(), TO-FROM)
        self.assertEqual(t.columns(), 1+1)
        self.assertSequenceEqual(t["X"], range(FROM, TO))

    def test_add_column_from_value(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", VALUE)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1+1)
        self.assertSequenceEqual(t["X"], [VALUE]*LEN)

    def test_add_column_from_function_zero_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", lambda n: [VALUE]*n)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1+1)
        self.assertSequenceEqual(t["X"], [VALUE]*LEN)

    def test_add_column_from_function_one_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", range(LEN))
        t.add_column("Y", lambda n, xs: [x+1 for x in xs], "X")

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1+2)
        self.assertSequenceEqual(t["Y"], [x+1 for x in range(LEN)])

    def test_add_column_from_algo(self):
        LEN=10
        A=list(range(200, 200+LEN))
        B=list(range(300, 300+LEN))

        t = table.Table(LEN)
        t.add_column("A", A)
        t.add_column("B", B)
        t.add_column("C", algo.by_row(lambda a, b: a+b), "A", "B")
        self.assertSequenceEqual(t["C"], list(range(500, 500+2*LEN, 2)))

    def test_add_column_reject_duplicate(self):
        """ add_column() should reject duplicate names.
        """
        t = table.Table(10)
        t.add_column("X", 1)
        with self.assertRaises(table.DuplicateName):
            t.add_column("X", 1)

    def test_naive_window(self):
        LEN=10
        A=list(range(10, 10+LEN))

        t = table.Table(LEN)
        t.add_column("A", A)
        t.add_column("B", algo.naive_window(sum, 2), "A")
        self.assertSequenceEqual(t["B"], [None, 21, 23, 25, 27, 29, 31, 33, 35, 37])

    def test_get_column(self):
        LEN=5
        A=[1]*LEN
        B=[2]*LEN
        C=[3]*LEN
        t = table.Table(LEN)

        t.add_column("A", A)
        t.add_column("B", B)
        t.add_column("C", C)

        # Column 0 is used for rows numbering
        self.assertEqual(t[1]._column, A)
        self.assertEqual(t[2]._column, B)
        self.assertEqual(t[3]._column, C)

        self.assertEqual(t["A"]._column, A)
        self.assertEqual(t["B"]._column, B)
        self.assertEqual(t["C"]._column, C)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def test_eval_from_callable(self):
        LEN=99
        VALUE=123

        t = table.Table(LEN)
        t.add_column("X", VALUE)
        result = t.eval(lambda n, xs:sum(xs), "X")

        self.assertEqual(result, VALUE*LEN)

    def test_eval_from_iterable(self):
        LEN=99

        r = range(LEN)
        t = table.Table(LEN)
        result = t.eval(r)

        self.assertEqual(len(result), LEN)
        self.assertSequenceEqual(result, list(r))

    def test_eval_from_column_ref(self):
        LEN=99
        VALUE="123"

        t = table.Table(LEN)
        t.add_column("X", algo.constantly(VALUE))
        result = t.eval(t["X"])

        self.assertEqual(len(result), LEN)
        self.assertSequenceEqual(result, t["X"])

    def test_bad_col_length(self):
        t = table.Table(99)

        with self.assertRaises(table.InvalidError):
            t.add_column("X", [0.0]*100)

        with self.assertRaises(table.InvalidError):
            t.add_column("X", [0.0]*98)

    def test_rename(self):
        t = table.Table(10)
        t.add_columns(
            ("A", lambda count : range(count)),
            ("B", 2),
            ("C", 3),
        )
        t.rename("A", "N")
        self.assertSequenceEqual(t.names(), ("#", "N", "B", "C"))

    def test_rename_column_0_is_protected(self):
        """ It should not allow renaming column zero.
        """
        t = table.Table(10)
        t.add_columns(
            ("A", 1),
        )
        with self.assertRaises(ValueError):
            t.rename("#", "N")
        with self.assertRaises(ValueError):
            t.rename(0, "N")

    def test_delete(self):
        t = table.Table(10)
        t.add_columns(
            ("A", lambda count : range(count)),
            ("B", 2),
            ("C", 3),
        )
        t.del_column("B")
        self.assertSequenceEqual(t.names(), ("#", "A", "C"))

    def test_delete_column_0_is_protected(self):
        """ It should not allow deleting column zero.
        """
        t = table.Table(10)
        t.add_columns(
            ("A", 1),
        )
        with self.assertRaises(ValueError):
            t.del_column("#")
        with self.assertRaises(ValueError):
            t.del_column(0)

    # ------------------------------------------------------------------
    # Transformations
    # ------------------------------------------------------------------
    def test_filter(self):
        """
        Row filtering
        """
        t = table.Table(10)
        t.add_columns(
            ("A", lambda count : range(count)),
            ("B", 2),
            ("C", 3),
        )
        t2 = t.filter(lambda x : 2 < x < 7, "A")
        self.assertEqual(t2.rows(), 4)
        self.assertSequenceEqual(list(t2["A"]), (3,4,5,6))

    # ------------------------------------------------------------------
    # Transformations
    # ------------------------------------------------------------------
    def test_select_by_column_name(self):
        """
        Column selection
        """
        t = table.Table(10)
        t.add_columns(
            ("A", 1),
            ("B", 2),
            ("C", 3),
            ("D", 3),
        )
        t2 = t.select("C","D","A")
        self.assertEqual(t2.rows(), t.rows())
        self.assertEqual(t2.columns(), 1+3)
        self.assertEqual(t2[1], t[3])
        self.assertEqual(t2[2], t[4])
        self.assertEqual(t2[3], t[1])

# ======================================================================
# Column refs
# ======================================================================
class TestColumnRef(unittest.TestCase):
    def test_add(self):
        FROM = 1
        TO = 101
        N = 2
        t = table.Table(TO-FROM)

        t.add_column("X", range(FROM, TO))
        col = t["X"]

        self.assertEqual(col+N, list(range(FROM+N, TO+N)))

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

# ======================================================================
# Row iterator
# ======================================================================
class TestTableRowIterator(unittest.TestCase):
    def setUp(self):
        self._table = table.Table(10)
        self._table.add_columns(
            ("A", range(100, 110)),
            ("B", range(200, 210)),
            ("C", range(300, 310)),
        )

    def test_iterator_all_columns(self):
        """
        Without a column selector is None, it returns a row iterator over
        the entire table.
        """
        actual = list(self._table.row_iterator())
        expected = list(zip(*self._table.data()))
        self.assertSequenceEqual(actual, expected)

    def test_iterator_none(self):
        """
        When the column selector is None, it returns a row iterator over
        the entire table.
        """
        actual = list(self._table.row_iterator(None))
        expected = list(zip(*self._table.data()))
        self.assertSequenceEqual(actual, expected)

    def test_iterator_col_list(self):
        """
        When the column selector is None, it returns a row iterator over
        the entire table.
        """
        actual = list(self._table.row_iterator(["C","C","A"]))
        A = self._table["A"]
        C = self._table["C"]
        expected = list(zip(C, C, A))
        self.assertSequenceEqual(actual, expected)

# ======================================================================
# Table join
# ======================================================================
class TestTableJoin(unittest.TestCase):
    def setUp(self):
        tableA = self._tableA = table.Table(10)
        self._tableA.add_columns(
            ("A", range(100, 110)),
            ("B", range(200, 210)),
            ("C", range(300, 310)),
        )
        tableB = self._tableB = table.Table(10)
        self._tableB.add_columns(
            ("U", range(100, 110)),
            ("V", range(600, 610)),
            ("W", range(700, 710)),
        )

        self._cols = dict(
                [(name, tableA[name]._column) for name in tableA.names()] +
                [(name, tableB[name]._column) for name in tableB.names()]
                )

    def test_join_0(self):
        t = table.join(self._tableA, self._tableB, "A", "U")
        expected = list(self._cols[k] for k in "ABCUVW")
        expected = [[*range(len(expected[0]))]] + expected
        self.assertSequenceEqual(t.data(), expected)

    def test_join_1(self):
        self._tableA["A"][2] = None
        self._tableB["U"][5] = None
        t = table.join(self._tableA, self._tableB, "A", "U")

        idx = iter(range(999))
        expected = list(zip(*[self._cols[k] for k in "ABCUVW"]))
        expected = [(next(idx), *r) for r in expected if None not in r]
        self.assertSequenceEqual(list(zip(*t.data())), expected)

    def test_join_2(self):
        self._tableA["A"][4] = None
        self._tableB["U"][3:6] = [None]*3
        t = table.join(self._tableA, self._tableB, "A", "U")

        idx = iter(range(999))
        expected = list(zip(*[self._cols[k] for k in "ABCUVW"]))
        expected = [(next(idx), *r) for r in expected if None not in r]
        self.assertSequenceEqual(list(zip(*t.data())), expected)

# ======================================================================
# CSV
# ======================================================================
class TestCSV(unittest.TestCase):
    def test_load(self):
        t = table.table_from_csv_file("tests/_fixtures/bd.csv", format="dn-n")

        self.assertEqual(t.rows(), 284)
        self.assertEqual(t.columns(), 1+3)

        time = t["time"]
        self.assertEqual(time[0], "2022-01-03")
        self.assertEqual(time[-1], "2023-02-07")

        quote = t["BOURSE DIRECT"]
        self.assertEqual(quote[0], 2.73)
        self.assertEqual(quote[-1], 3.49)

