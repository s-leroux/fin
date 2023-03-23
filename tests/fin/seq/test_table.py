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
        self.assertEqual(t.columns(), 0)

    def test_add_column_from_iterator(self):
        FROM=1
        TO=100
        t = table.Table(TO-FROM)

        t.add_column(table.Column("X", range(FROM, TO)))

        self.assertEqual(t.rows(), TO-FROM)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"], range(FROM, TO))

    def test_add_column_from_value(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", VALUE)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"], [VALUE]*LEN)

    def test_add_column_from_function_zero_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", lambda n: [VALUE]*n)

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 1)
        self.assertSequenceEqual(t["X"], [VALUE]*LEN)

    def test_add_column_from_function_one_param(self):
        LEN=99
        VALUE=123
        t = table.Table(LEN)

        t.add_column("X", range)
        t.add_column("Y", (lambda n, xs: [x+1 for x in xs], "X"))

        self.assertEqual(t.rows(), LEN)
        self.assertEqual(t.columns(), 2)
        self.assertSequenceEqual(t["Y"], [x+1 for x in range(LEN)])

    def test_add_column_from_other_table(self):
        LEN=99
        t1 = table.Table(LEN)
        t1.add_column("X", range)

        t2 = table.Table(LEN)
        t2.add_column(t1["X"])

        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2["X"], t1["X"])

    def test_add_column_from_algo(self):
        LEN=10
        A=list(range(200, 200+LEN))
        B=list(range(300, 300+LEN))

        t = table.Table(LEN)
        t.add_column(table.Column("A", A))
        t.add_column(table.Column("B", B))
        t.add_column("C", (algo.by_row(lambda a, b: a+b), "A", "B"))
        self.assertSequenceEqual(t["C"], list(range(500, 500+2*LEN, 2)))

    def test_add_column_reject_duplicate(self):
        """ add_column() should reject duplicate names.
        """
        t = table.Table(10)
        t.add_column("X", 1)
        with self.assertRaises(table.DuplicateName):
            t.add_column("X", 1)

    def test_add_columns_name_expr(self):
        """
        Table.add_columns() should accept (name, expr) pairs as arguments.
        """
        LEN=10
        t = table.Table(LEN)
        t.add_columns(
                ("X", range),
                ("Y", 2),
                )

        self.assertEqual(t.columns(), 2)
        self.assertSequenceEqual(t["X"], [*range(LEN)])
        self.assertSequenceEqual(t["Y"], [2]*LEN)

    def test_add_columns_column(self):
        """
        Table.add_columns() should accept Column instances as arguments.
        """
        LEN=10
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", range),
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
        t.add_column(table.Column("A", A))
        t.add_column("B", (algo.naive_window(sum, 2), "A"))
        self.assertSequenceEqual(t["B"], [None, 21, 23, 25, 27, 29, 31, 33, 35, 37])

    def test_get_column(self):
        LEN=5
        A=[1]*LEN
        B=[2]*LEN
        C=[3]*LEN
        t = table.Table(LEN)

        t.add_column(table.Column("A", A))
        t.add_column(table.Column("B", B))
        t.add_column(table.Column("C", C))

        # Column 0 is used for rows numbering
        self.assertEqual(t[0].values, A)
        self.assertEqual(t[1].values, B)
        self.assertEqual(t[2].values, C)
        self.assertEqual(t[0].name, "A")
        self.assertEqual(t[1].name, "B")
        self.assertEqual(t[2].name, "C")

        self.assertEqual(t["A"], t[0])
        self.assertEqual(t["B"], t[1])
        self.assertEqual(t["C"], t[2])

    def test_bad_col_length(self):
        t = table.Table(99)

        with self.assertRaises(table.InvalidError):
            t.add_column(table.Column("X", [0.0]*100))

        with self.assertRaises(table.InvalidError):
            t.add_column(table.Column("X", [0.0]*98))

    def test_rename(self):
        t = table.Table(10)
        t.add_columns(
            ("A", range),
            ("B", 2),
            ("C", 3),
        )
        t.rename("A", "N")
        self.assertSequenceEqual(t.names(), ("N", "B", "C"))

    def test_delete(self):
        t = table.Table(10)
        t.add_columns(
            ("A", lambda count : range(count)),
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
                ("X", range),
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
                ("X", limit),
                ("Y", limit),
                ("Z", limit),
                )
        t2 = t1.lstrip()
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2.rows(), t1.rows()-LIMIT)
        self.assertSequenceEqual(t2["X"].values, [*range(LIMIT, LEN)])
        self.assertSequenceEqual(t2["Y"].values, [*range(LIMIT, LEN)])
        self.assertSequenceEqual(t2["Z"].values, [*range(LIMIT, LEN)])

    def test_sort(self):
        LEN=10000
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", range),
                ("Y", lambda n : [*range(n,0,-1)]),
                )
        t2 = t1.sort("Y")
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertEqual(t2.rows(), t1.rows())
        self.assertSequenceEqual(t2["Y"].values, [*range(1, LEN+1, 1)])

    def test_group(self):
        LEN=40
        t1 = table.Table(LEN)
        t1.add_columns(
                ("X", lambda n : [x//5 for x in range(n)]),
                ("Y1", range),
                ("Y2", range),
                ("Y3", range),
                ("Z", lambda n : [x//10 for x in range(n)]),
                )
        t2 = t1.group("X", dict(
            Y1=min,
            Y2=max,
            Y3=sum,
            ))
        self.assertIsNot(t2, t1)
        self.assertEqual(t2.columns(), t1.columns())
        self.assertSequenceEqual(t2["X"], [*range(LEN//5)])
        self.assertSequenceEqual(t2["Y1"], [x*5 for x in range(LEN//5)])
        self.assertSequenceEqual(t2["Y2"], [x*5+4 for x in range(LEN//5)])
        self.assertSequenceEqual(t2["Y3"], [x*5*5+10 for x in range(LEN//5)])


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
        self.assertEqual(self._table.reval(1), [ table.C([1]*self._table.rows()) ])
        self.assertEqual(self._table.reval(2.50), [ table.C([2.50]*self._table.rows()) ])

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
        expected = [ list(range(self._table.rows())) ]
        actual = [column.values for column in self._table.reval(range)]

        self.assertEqual(actual, expected)

    def test_reval_dictionary(self):
        """
        Dictionary
        """
        NAME="Test"
        expected = table.Column(NAME, [ a+b for a,b in zip(self._A, self._B)])
        fct = lambda rowcount, col_a, col_b : [ a+b for a,b in zip(col_a, col_b) ]

        actual, = self._table.reval({"name": NAME, "expr": (fct, "A", "B")})

        self.assertEqual(actual, expected)

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

# ======================================================================
# Row iterator
# ======================================================================
class TestTableRowIterator(unittest.TestCase):
    def setUp(self):
        rng = lambda start : lambda rowcount : range(start, start+rowcount)

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
    def setUp(self):
        rng = lambda start : lambda rowcount : range(start, start+rowcount)

        tableA = self._tableA = table.Table(10)
        self._tableA.add_columns(
            ("A", rng(100)),
            ("B", rng(200)),
            ("C", rng(300)),
        )
        tableB = self._tableB = table.Table(10)
        self._tableB.add_columns(
            ("U", rng(100)),
            ("V", rng(600)),
            ("W", rng(700)),
        )

        self._cols = dict(
                [(name, tableA[name]) for name in tableA.names()] +
                [(name, tableB[name]) for name in tableB.names()]
                )

    def test_join_0(self):
        t = table.join(self._tableA, self._tableB, "A", "U")
        expected = list(self._cols[k].values for k in "ABCUVW")
        self.assertSequenceEqual(t.data(), expected)

    def test_join_1(self):
        self._tableA["A"].values[2] = None
        self._tableB["U"].values[5] = None
        t = table.join(self._tableA, self._tableB, "A", "U")

        expected = list(zip(*[self._cols[k] for k in "ABCUVW"]))
        expected = [r for r in expected if None not in r]
        self.assertSequenceEqual(list(zip(*t.data())), expected)

    def test_join_2(self):
        self._tableA["A"].values[4] = None
        self._tableB["U"].values[3:6] = [None]*3
        t = table.join(self._tableA, self._tableB, "A", "U")

        expected = list(zip(*[self._cols[k] for k in "ABCUVW"]))
        expected = [r for r in expected if None not in r]
        self.assertSequenceEqual(list(zip(*t.data())), expected)

# ======================================================================
# 
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
        self.assertSequenceEqual(S, [a+1.0 for a in A])

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

