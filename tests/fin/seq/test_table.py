import unittest

from fin.seq import column
from fin.seq import expr
from fin.seq import table
from fin.seq import algo

# ======================================================================
# Test table
# ======================================================================
class TestTable(unittest.TestCase):
    def test_constructor(self):
        t = table.Table(0)

        self.assertEqual(t.rows(), 0)
        self.assertEqual(t.columns(), 0)

    def test_add_column_from_iterator(self):
        FROM=1
        TO=100
        t = table.Table(TO-FROM)

        t.add_column(column.Column.from_sequence("X", range(FROM, TO)))

        self.assertEqual(t.rows(), TO-FROM)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"].py_values, range(FROM, TO))

    def test_add_column_from_value(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", expr.constant(VALUE))

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"].py_values, [VALUE]*LEN)

    def test_add_column_from_function_zero_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", expr.constant(VALUE))

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"].py_values, [VALUE]*LEN)

    def test_add_column_from_function_one_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", expr.apply(range))
        t.add_column("Y", (expr.apply(lambda n, xs: [x+1 for x in xs]), "X"))

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 2)
        self.assertSequenceEqual(t["Y"].py_values, [x+1 for x in range(LEN)])

    def test_add_column_from_other_table(self):
        LEN=99
        t1 = table.Table(LEN)
        t1.add_column("X", expr.apply(range))

        t2 = table.Table(LEN)
        t2.add_column(t1["X"])

        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2["X"], t1["X"])

    def test_add_column_from_algo(self):
        LEN=10
        f = lambda a, b: a+b

        t = table.Table(LEN, columns=dict(
            A=expr.ramp(200),
            B=expr.ramp(300),
            C=(algo.by_row(f), "A", "B"),
            ))
        self.assertSequenceEqual(t["C"].py_values, [f(a,b) for a,b in zip(t["A"],t["B"])])

    def test_add_column_reject_duplicate(self):
        """ add_column() should reject duplicate names.
        """
        t = table.Table(10, columns=dict(
            X=1,
            ))
        with self.assertRaises(table.DuplicateName):
            t.add_column("X", 1)

    def test_add_columns_name_expr(self):
        """
        Table.add_columns() should accept (name, expr) pairs as arguments.
        """
        LEN=10
        t = table.Table(LEN)
        t.add_columns(
                ("X", expr.apply(range)),
                ("Y", 2),
                )

        self.assertEqual(t.columns(), 2)
        self.assertSequenceEqual(t["X"].py_values, [*range(LEN)])
        self.assertSequenceEqual(t["Y"].py_values, [2]*LEN)

    def test_add_columns_column(self):
        """
        Table.add_columns() should accept Column instances as arguments.
        """
        LEN=10
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", expr.apply(range)),
                ("Y", 2),
                )
        t2 = table.Table(LEN)
        t2.add_columns(
                t1["X"],
                t1["Y"],
                )
        self.assertEqual(t2.columns(), t1.columns())
        self.assertSequenceEqual(t2["X"], t1["X"])
        self.assertSequenceEqual(t2["Y"], t1["Y"])

    def test_naive_window(self):
        LEN=10
        A=list(range(10, 10+LEN))

        t = table.Table(LEN)
        t.add_column(column.Column.from_sequence("A", A))
        t.add_column("B", (algo.naive_window(sum, 2), "A"))
        self.assertSequenceEqual(t["B"].py_values, [None, 21, 23, 25, 27, 29, 31, 33, 35, 37])

    def test_get_column(self):
        LEN=5
        A=(1,)*LEN
        B=(2,)*LEN
        C=(3,)*LEN
        t = table.Table(LEN)

        t.add_column(column.Column.from_sequence("A", A))
        t.add_column(column.Column.from_sequence("B", B))
        t.add_column(column.Column.from_sequence("C", C))

        # Column 0 is used for rows numbering
        self.assertEqual(t[0].py_values, A)
        self.assertEqual(t[1].py_values, B)
        self.assertEqual(t[2].py_values, C)
        self.assertEqual(t[0].name, "A")
        self.assertEqual(t[1].name, "B")
        self.assertEqual(t[2].name, "C")

        self.assertEqual(t["A"], t[0])
        self.assertEqual(t["B"], t[1])
        self.assertEqual(t["C"], t[2])

    def test_bad_col_length(self):
        t = table.Table(99)

        with self.assertRaises(table.InvalidError):
            t.add_column(column.Column.from_sequence("X", [0.0]*100))

        with self.assertRaises(table.InvalidError):
            t.add_column(column.Column.from_sequence("X", [0.0]*98))

    def test_rename(self):
        t = table.Table(10)
        t.add_columns(
            ("A", expr.apply(range)),
            ("B", 2),
            ("C", 3),
        )
        t.rename("A", "N")
        self.assertSequenceEqual(t.names(), ("N", "B", "C"))

    def test_delete(self):
        t = table.Table(10)
        t.add_columns(
            ("A", expr.apply(range)),
            ("B", 2),
            ("C", 3),
        )
        t.del_column("B")
        self.assertSequenceEqual(t.names(), ("A", "C"))

    # ------------------------------------------------------------------
    # Transformations
    # ------------------------------------------------------------------
    def test_filter(self):
        """
        Row filtering
        """
        t = table.Table(10)
        t.add_columns(
            ("A", expr.apply(range)),
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
        self.assertEqual(t2.columns(), 3)
        self.assertEqual(t2[0], t[2])
        self.assertEqual(t2[1], t[3])
        self.assertEqual(t2[2], t[0])

    def test_copy(self):
        """
        Table.copy() should return a new table with the same columns as the receiver.
        """
        LEN=10
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", expr.apply(range)),
                ("Y", 2),
                )

        t2 = t1.copy()

        self.assertIsNot(t2, t1)
        self.assertEqual(t2.rows(), t1.rows())
        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2["X"], t1["X"])
        self.assertEqual(t2["X"], t1["X"])
        self.assertEqual(t2["Y"], t1["Y"])

    def test_ltrip(self):
        LEN=10
        LIMIT=3
        limit=lambda n : [None if x < LIMIT else x for x in range(n)]
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", expr.apply(limit)),
                ("Y", expr.apply(limit)),
                ("Z", expr.apply(limit)),
                )
        t2 = t1.lstrip()
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2.rows(), t1.rows()-LIMIT)
        self.assertSequenceEqual(t2["X"].py_values, [*range(LIMIT, LEN)])
        self.assertSequenceEqual(t2["Y"].py_values, [*range(LIMIT, LEN)])
        self.assertSequenceEqual(t2["Z"].py_values, [*range(LIMIT, LEN)])

    def test_sort(self):
        LEN=10000
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", expr.call(range)),
                ("Y", expr.apply(lambda n : [*range(n,0,-1)])),
                )
        t2 = t1.sort("Y")
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2.rows(), t1.rows())
        self.assertSequenceEqual(t2["Y"].py_values, [*range(1, LEN+1, 1)])

    def test_group(self):
        LEN=40
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", expr.call(lambda n : [x//5 for x in range(n)])),
                ("Y1", expr.call(range)),
                ("Y2", expr.call(range)),
                ("Y3", expr.call(range)),
                ("Z", expr.call(lambda n : [x//10 for x in range(n)])),
                )
        t2 = t1.group("X", dict(
            Y1=min,
            Y2=max,
            Y3=sum,
            ))
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertSequenceEqual(t2["X"].py_values, [*range(LEN//5)])
        self.assertSequenceEqual(t2["Y1"].py_values, [x*5 for x in range(LEN//5)])
        self.assertSequenceEqual(t2["Y2"].py_values, [x*5+4 for x in range(LEN//5)])
        self.assertSequenceEqual(t2["Y3"].py_values, [x*5*5+10 for x in range(LEN//5)])


# ======================================================================
# Table expression evaluation
# ======================================================================
class TestTableExpressionEvaluation(unittest.TestCase):
    def setUp(self):
        t = self._table = table.Table(10)
        self._table.add_columns(
            ("A", 1),
            ("B", 2),
            ("C", 3),
            ("D", 3),
        )
        
        self._A = t["A"]
        self._B = t["B"]
        self._C = t["C"]
        self._D = t["D"]

        self._f0 = lambda rowcount, col, *cols : col
        self._f1 = lambda rowcount, x, col, *cols : col
        self._f2 = lambda rowcount, x, y, col, *cols : col
        self._f3 = lambda rowcount, x, y, z, col, *cols : col

    def test_reval_column_constant(self):
        """
        Constant (numeric) columns
        """
        # Individual column selection
        self.assertEqual(self._table.reval(1), [ column.Column.from_sequence("", [1]*self._table.rows()) ])
        self.assertEqual(self._table.reval(2.50), [ column.Column.from_sequence("", [2.50]*self._table.rows()) ])

    def test_reval_column_name(self):
        """
        Column selection by name
        """
        # Individual column selection
        self.assertEqual(self._table.reval("A"), [ self._A ])
        self.assertEqual(self._table.reval("B"), [ self._B ])
        self.assertEqual(self._table.reval("C"), [ self._C ])
        self.assertEqual(self._table.reval("D"), [ self._D ])

        # multi-column selection
        self.assertEqual(self._table.reval("A", "B"), [ self._A, self._B ])
        self.assertEqual(self._table.reval("B", "C", "D"), [ self._B, self._C, self._D ])

        # group selection
        self.assertEqual(self._table.reval(("B", "C"), "D"), [ self._B, self._C, self._D ])
        self.assertEqual(self._table.reval("B", ("C", "D")), [ self._B, self._C, self._D ])

    def test_reval_function_call(self):
        """
        Function calls
        """
        # Basic function calls
        self.assertEqual(self._table.reval(self._f0, "A", "B"), [ self._A ])
        self.assertEqual(self._table.reval(self._f1, "A", "B"), [ self._B ])

        # Nested function calls
        self.assertEqual(self._table.reval(self._f0, (self._f0, "A", "B", "C")), [ self._A ])
        self.assertEqual(self._table.reval(self._f0, (self._f2, "A", "B", "C")), [ self._C ])
        self.assertEqual(self._table.reval(self._f0, (self._f1, "A", "B"), "C"), [ self._B ])
        self.assertEqual(self._table.reval(self._f1, (self._f1, "A", "B"), "C"), [ self._C ])

        # Flat function calls
        self.assertEqual(self._table.reval(self._f0, self._f0, "A", "B", "C"), [ self._A ])
        self.assertEqual(self._table.reval(self._f0, self._f1, "A", "B", "C"), [ self._B ])
        self.assertEqual(self._table.reval(self._f0, self._f2, "A", "B", "C"), [ self._C ])

    def test_reval_generator(self):
        """
        Generators
        """
        LEN=self._table.rows()
        g = lambda : (i*i for i in range(LEN))
        expected = [*g()]
        [actual] = self._table.reval(expr.iterable(g()))

        self.assertSequenceEqual(actual.py_values, expected)

    def test_reval_dictionary(self):
        """
        Dictionary
        """
        NAME="Test"
        expected = column.Column.from_sequence(NAME, [ a+b for a,b in zip(self._A, self._B)])
        fct = lambda rowcount, col_a, col_b : [ a+b for a,b in zip(col_a, col_b) ]

        actual, = self._table.reval({"name": NAME, "expr": (expr.apply(fct), "A", "B")})

        self.assertEqual(actual.py_values, expected.py_values)
        self.assertEqual(actual.name, NAME)

# ======================================================================
# Row iterator
# ======================================================================
class TestTableRowIterator(unittest.TestCase):
    def setUp(self):
        rng = expr.ramp

        self._table = table.Table(10)
        self._table.add_columns(
            ("A", rng(100)),
            ("B", rng(200)),
            ("C", rng(300)),
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
    def build_tables(self, *args):
        LEN=10
        def rng(start):
            return list(range(start, start+LEN))

        data = dict(
            A=rng(100),
            B=rng(200),
            C=rng(300),
            U=rng(100),
            V=rng(600),
            W=rng(700),
        )

        while args:
            col, idx, val, *args = args
            data[col][idx] = val

        cols = { name: column.Column.from_sequence(name, data[name]) for name in "ABCUVW" }
        tableA = table.Table(10)
        tableA.add_columns(
            ("A", cols["A"]),
            ("B", cols["B"]),
            ("C", cols["C"]),
        )
        tableB = table.Table(10)
        tableB.add_columns(
            ("U", cols["U"]),
            ("V", cols["V"]),
            ("W", cols["W"]),
        )

        return cols, tableA, tableB

    def test_join_0(self):
        """
        Both the inner- and outer-join should produce the same result when key columns match.
        """
        cols, tableA, tableB = self.build_tables()

        expected = [ cols[k].py_values for k in "AUBCVW" ]
        with self.subTest(join="inner join"):
            t = table.join(tableA, tableB, "A", "U")
            self.assertSequenceEqual(t.data(), expected)
        with self.subTest(join="outer join"):
            t = table.outer_join(tableA, tableB, "A", "U")
            self.assertSequenceEqual(t.data(), expected)

    def test_join_1(self):
        """
        When a key is missing in only one table, the inner join should discard the row
        but the outer join should keep it.
        """
        cols, tableA, tableB = self.build_tables(
                "A", 2, None,
                "U", 5, None,
                )

        with self.subTest(join="inner join"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (103,  103,  203,  303,  603,  703),
                (104,  104,  204,  304,  604,  704),
                (106,  106,  206,  306,  606,  706),
                (107,  107,  207,  307,  607,  707),
                (108,  108,  208,  308,  608,  708),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.join(tableA, tableB, "A", "U")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (None, 102,  None, None, 602,  702),
                (103,  103,  203,  303,  603,  703),
                (104,  104,  204,  304,  604,  704),
                (105,  None, 205,  305,  None, None),
                (106,  106,  206,  306,  606,  706),
                (107,  107,  207,  307,  607,  707),
                (108,  108,  208,  308,  608,  708),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.outer_join(tableA, tableB, "A", "U")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join w/propagate"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (None, 102,  201,  301,  602,  702),
                (103,  103,  203,  303,  603,  703),
                (104,  104,  204,  304,  604,  704),
                (105,  None, 205,  305,  604,  704),
                (106,  106,  206,  306,  606,  706),
                (107,  107,  207,  307,  607,  707),
                (108,  108,  208,  308,  608,  708),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.outer_join(tableA, tableB, "A", "U", propagate=True)
            self.assertSequenceEqual([*t.row_iterator()], expected)

    def test_join_2(self):
        """
        When a key is None in both tables, it should be discarded.
        """
        self.maxDiff = None
        cols, tableA, tableB = self.build_tables(
                "A", 4, None,
                "A", 7, None,
                "A", 8, None,
                "U", 3, None,
                "U", 4, None,
                "U", 5, None,
                )

        with self.subTest(join="inner join"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (102,  102,  202,  302,  602,  702),
                (106,  106,  206,  306,  606,  706),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.join(tableA, tableB, "A", "U")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (102,  102,  202,  302,  602,  702),
                (103,  None, 203,  303,  None, None),
                (105,  None, 205,  305,  None, None),
                (106,  106,  206,  306,  606,  706),
                (None, 107, None, None,  607,  707),
                (None, 108, None, None,  608,  708),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.outer_join(tableA, tableB, "A", "U")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join w/propagate"):
            expected = [
                (100,  100,  200,  300,  600,  700),
                (101,  101,  201,  301,  601,  701),
                (102,  102,  202,  302,  602,  702),
                (103,  None, 203,  303,  602,  702),
                (105,  None, 205,  305,  602,  702),
                (106,  106,  206,  306,  606,  706),
                (None, 107,  206,  306,  607,  707),
                (None, 108,  206,  306,  608,  708),
                (109,  109,  209,  309,  609,  709)
             ]
            t = table.outer_join(tableA, tableB, "A", "U", propagate=True)
            self.assertSequenceEqual([*t.row_iterator()], expected)

    def test_join_at_end(self):
        """
        Check that joining disjoint tables produces the expected result.
        """
        self.maxDiff = None
        cols, tableA, tableB = self.build_tables(
                "A", 4, None,
                "A", 7, None,
                "A", 8, None,
                "U", 3, None,
                "U", 4, None,
                "U", 5, None,
                )

        ta = tableA.select("B", "C")
        tb = tableB.select("V", "W")

        with self.subTest(join="inner join"):
            expected = [
             ]
            t = table.join(ta, tb, "B", "V")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (200,  None,  300,  None,),
                (201,  None,  301,  None,),
                (202,  None,  302,  None,),
                (203,  None,  303,  None,),
                (204,  None,  304,  None,),
                (205,  None,  305,  None,),
                (206,  None,  306,  None,),
                (207,  None,  307,  None,),
                (208,  None,  308,  None,),
                (209,  None,  309,  None,),
                (None, 600,   None,  700),
                (None, 601,   None,  701),
                (None, 602,   None,  702),
                (None, 603,   None,  703),
                (None, 604,   None,  704),
                (None, 605,   None,  705),
                (None, 606,   None,  706),
                (None, 607,   None,  707),
                (None, 608,   None,  708),
                (None, 609,   None,  709),
             ]
            t = table.outer_join(ta, tb, "B", "V")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join w/propagate"):
            expected = [
                (200,  None,  300,  None,),
                (201,  None,  301,  None,),
                (202,  None,  302,  None,),
                (203,  None,  303,  None,),
                (204,  None,  304,  None,),
                (205,  None,  305,  None,),
                (206,  None,  306,  None,),
                (207,  None,  307,  None,),
                (208,  None,  308,  None,),
                (209,  None,  309,  None,),
                (None, 600,   309,  700),
                (None, 601,   309,  701),
                (None, 602,   309,  702),
                (None, 603,   309,  703),
                (None, 604,   309,  704),
                (None, 605,   309,  705),
                (None, 606,   309,  706),
                (None, 607,   309,  707),
                (None, 608,   309,  708),
                (None, 609,   309,  709),
             ]
            t = table.outer_join(ta, tb, "B", "V", propagate=True)
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (None, 200,  None,  300,),
                (None, 201,  None,  301,),
                (None, 202,  None,  302,),
                (None, 203,  None,  303,),
                (None, 204,  None,  304,),
                (None, 205,  None,  305,),
                (None, 206,  None,  306,),
                (None, 207,  None,  307,),
                (None, 208,  None,  308,),
                (None, 209,  None,  309,),
                (600,  None,  700,  None,),
                (601,  None,  701,  None,),
                (602,  None,  702,  None,),
                (603,  None,  703,  None,),
                (604,  None,  704,  None,),
                (605,  None,  705,  None,),
                (606,  None,  706,  None,),
                (607,  None,  707,  None,),
                (608,  None,  708,  None,),
                (609,  None,  709,  None,),
             ]
            t = table.outer_join(tb, ta, "V", "B")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (None, 200,  None,  300,),
                (None, 201,  None,  301,),
                (None, 202,  None,  302,),
                (None, 203,  None,  303,),
                (None, 204,  None,  304,),
                (None, 205,  None,  305,),
                (None, 206,  None,  306,),
                (None, 207,  None,  307,),
                (None, 208,  None,  308,),
                (None, 209,  None,  309,),
                (600,  None,  700,  309,),
                (601,  None,  701,  309,),
                (602,  None,  702,  309,),
                (603,  None,  703,  309,),
                (604,  None,  704,  309,),
                (605,  None,  705,  309,),
                (606,  None,  706,  309,),
                (607,  None,  707,  309,),
                (608,  None,  708,  309,),
                (609,  None,  709,  309,),
             ]
            t = table.outer_join(tb, ta, "V", "B", propagate=True)
            self.assertSequenceEqual([*t.row_iterator()], expected)

    def test_outer_join_extend(self):
        """
        A common use case for outer_join() is to extend a table by adding
        more rows. We check that here.
        """
        self.maxDiff = None

        ta = table.table_from_dict({
            "T": [*range(300,305), *range(500, 505), *range(600,605)]
            })
        tb = table.table_from_dict({
            "T": [*range(100,105), *range(500, 505), *range(700,705)]
            })

        with self.subTest(join="inner join"):
            expected = [
                (500,),
                (501,),
                (502,),
                (503,),
                (504,),
             ]
            t = table.join(ta, tb, "T", "T")
            self.assertSequenceEqual([*t.row_iterator()], expected)
        with self.subTest(join="outer join"):
            expected = [
                (100,),
                (101,),
                (102,),
                (103,),
                (104,),
                (300,),
                (301,),
                (302,),
                (303,),
                (304,),
                (500,),
                (501,),
                (502,),
                (503,),
                (504,),
                (600,),
                (601,),
                (602,),
                (603,),
                (604,),
                (700,),
                (701,),
                (702,),
                (703,),
                (704,),
             ]
            t = table.outer_join(ta, tb, "T", "T")
            self.assertSequenceEqual([*t.row_iterator()], expected)
            self.assertSequenceEqual(t.names(), ("T",))
            t = table.outer_join(tb, ta, "T", "T")
            self.assertSequenceEqual([*t.row_iterator()], expected)
            self.assertSequenceEqual(t.names(), ("T",))

    def test_join_rename(self):
        """
        When the source tables are named, the column in the result table
        are renamed accordingly.
        """
        cols, tableA, tableB = self.build_tables(
                "A", 4, None,
                "A", 7, None,
                "A", 8, None,
                "U", 3, None,
                "U", 4, None,
                "U", 5, None,
                )
        tableA._name="TA"
        tableB._name="TB"

        for fct in (table.join, table.outer_join):
            with self.subTest(join="join no rename", fct=fct):
                expected = ["A","U","B","C","V","W"]
                t = fct(tableA, tableB, "A", "U", rename=False)
                self.assertSequenceEqual(t.names(), expected)

            with self.subTest(join="join w/rename", fct=fct):
                expected = ["TA:A","TB:U","TA:B","TA:C","TB:V","TB:W"]
                t = fct(tableA, tableB, "A", "U")
                self.assertSequenceEqual(t.names(), expected)

            tableC = tableA.copy(name="TC")
            with self.subTest(join="join w/rename using common column", fct=fct):
                expected = ["A","TA:B","TA:C","TC:B","TC:C"]
                t = fct(tableA, tableC, "A")
                self.assertSequenceEqual(t.names(), expected)

# ======================================================================
# Table factories
# ======================================================================
class TestFromDict(unittest.TestCase):
    def test_load(self):
        LEN = 10
        A = [*range(LEN)]
        B = [1.0]*LEN
        t = table.table_from_dict(dict(
            A=A,
            B=B,
            ))

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 2)
        [S] = t.reval(algo.by_row(lambda a, b: a+b), "A", "B")
        self.assertSequenceEqual(S.py_values, [a+1.0 for a in A])

class TestAsTable(unittest.TestCase):
    def test_from_something(self):
        use_cases = (
                table.Table(5),
                dict(a=[1,2,3,4,5]),
                )
        for something in use_cases:
            with self.subTest(type=type(something)):
                t = table.as_table(something)
                self.assertEqual(type(t), table.Table)

# ======================================================================
# CSV
# ======================================================================
class TestCSV(unittest.TestCase):
    def test_load(self):
        t = table.table_from_csv_file("tests/_fixtures/bd.csv", format="dn-n")

        self.assertEqual(t.rows(), 284)
        self.assertEqual(t.columns(), 3)

        time = t["time"]
        self.assertEqual(str(time[0]), "2022-01-03")
        self.assertEqual(str(time[-1]), "2023-02-07")

        quote = t["BOURSE DIRECT"]
        self.assertEqual(quote[0], 2.73)
        self.assertEqual(quote[-1], 3.49)

