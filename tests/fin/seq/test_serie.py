import unittest

from fin.seq import serie
from fin.seq import column
from fin.seq import fc
from fin.seq import ag

# ======================================================================
# Core Serie functionalities
# ======================================================================
class TestSerie(unittest.TestCase):
    def test_create_serie_from_lists(self):
        """
        You can create a serie from lists.
        """
        ser = serie.Serie.create(fc.sequence("ABC"), fc.sequence([10, 20, 30]))

        self.assertIsInstance(ser.index, column.Column)
        self.assertSequenceEqual(ser.index.py_values, "ABC")

        c0, = ser.columns
        self.assertIsInstance(c0, column.Column)
        self.assertSequenceEqual(c0.py_values, [10, 20, 30])

    def test_add_scalar(self):
        """
        You can add a scalar to a serie.
        """
        seqA = [10, 20, 30, 40, 50]
        serA = serie.Serie.create(fc.sequence("ABCDF"), fc.sequence(seqA))
        scalar = 3

        serB = serA + scalar
        self.assertSequenceEqual(serB.index.py_values, "ABCDF")
        self.assertEqual(len(serB.columns), 1)
        self.assertSequenceEqual(serB.columns[0].f_values, [x+scalar for x in seqA])

    def test_add_series(self):
        """
        Adding two sequences performs an implicit join.
        """
        serA = serie.Serie.create(fc.sequence("ABCDF"), fc.sequence([10, 20, 30, 40, 50]))
        serB = serie.Serie.create(fc.sequence("ABCEF"), fc.sequence([11, 21, 31, 41, 51]))

        serC = serA + serB
        self.assertSequenceEqual(serC.index.py_values, "ABCF")
        self.assertEqual(len(serC.columns), 1)
        self.assertSequenceEqual(serC.columns[0].f_values, (21.0, 41.0, 61.0, 101.0))

    def test_get_by_index(self):
        """
        You can use the subscript notation to extract a sub-serie.
        """
        c1 = column.Column.from_sequence(range(10), name="a")
        c2 = column.Column.from_callable(lambda x : x*10, c1, name="b")
        c3 = column.Column.from_callable(lambda x : x*10, c2, name="c")
        cols = (c1, c2, c3)

        ser = serie.Serie.create(*cols)

        for idx, col in enumerate(cols):
            res = ser[idx]
            self.assertIsInstance(res, serie.Serie)
            self.assertEqual(res.index, c1)
            self.assertEqual(len(res.columns), 1)
            self.assertEqual(res.columns[0], col)

    def test_get_by_negative_index(self):
        """
        You can use the subscript notation to extract a sub-serie.
        """
        c1 = column.Column.from_sequence(range(10), name="a")
        c2 = column.Column.from_callable(lambda x : x*10, c1, name="b")
        c3 = column.Column.from_callable(lambda x : x*10, c2, name="c")
        cols = (c1, c2, c3)

        ser = serie.Serie.create(*cols)
        res = ser[-1]

        self.assertIsInstance(res, serie.Serie)
        self.assertEqual(res.index, c1)
        self.assertEqual(res.columns[0], c3)

    def test_get_by_name(self):
        """
        You can use the subscript notation to extract a sub-serie.
        """
        c1 = column.Column.from_sequence(range(10), name="a")
        c2 = column.Column.from_callable(lambda x : x*10, c1, name="b")
        c3 = column.Column.from_callable(lambda x : x*10, c2, name="c")
        cols = (c1, c2, c3)

        ser = serie.Serie.create(*cols)

        for idx, col in enumerate(cols):
            res = ser[col.name]
            self.assertIsInstance(res, serie.Serie)
            self.assertEqual(res.index, c1)
            self.assertEqual(len(res.columns), 1)
            self.assertEqual(res.columns[0], col)

    def test_get_items(self):
        """
        You can use the subscript notation to extract a sub-serie.
        """
        c1 = column.Column.from_sequence(range(10), name="a")
        c2 = column.Column.from_callable(lambda x : x*10, c1, name="b")
        c3 = column.Column.from_callable(lambda x : x*10, c2, name="c")
        cols = (c1, c2, c3)

        ser = serie.Serie.create(*cols)
        res = ser["a","c",1]

        self.assertIsInstance(res, serie.Serie)
        self.assertEqual(res.index, c1)
        self.assertEqual(len(res.columns), 3)
        self.assertEqual(res.columns[0], c1)
        self.assertEqual(res.columns[1], c3)
        self.assertEqual(res.columns[2], c2)

    def test_clear(self):
        """
        You can use the clear() method to return a serie containing only the index.
        """
        c1 = column.Column.from_sequence(range(10), name="a")
        c2 = column.Column.from_callable(lambda x : x*10, c1, name="b")
        c3 = column.Column.from_callable(lambda x : x*10, c2, name="c")
        cols = (c1, c2, c3)

        ser = serie.Serie.create(*cols)
        res = ser.clear()

        self.assertIsInstance(res, serie.Serie)
        self.assertEqual(res.index, c1)
        self.assertEqual(len(res.columns), 0)

# ======================================================================
# Joins
# ======================================================================
from enum import Enum
class TestJoin(unittest.TestCase):
    class Join(Enum):
        INNER_JOIN =        (0, serie.inner_join)
        FULL_OUTER_JOIN =   (1, serie.full_outer_join)
        LEFT_OUTER_JOIN =   (2, serie.left_outer_join)

    def run_join_engine(self, join):
        XX=None
        testcases = (
                (
                    # Simple case: identical indices
                    "ABCEF", [10, 11, 12, 13, 14], 
                    "ABCEF", [20, 21, 22, 23, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [20, 21, 22, 23, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [20, 21, 22, 23, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [20, 21, 22, 23, 24],
                ),
                (
                    # Trailing rows in A
                    "ABCEFGH", [10, 11, 12, 13, 14, 15, 16], 
                    "ABCEF", [20, 21, 22, 23, 24],
                    "ABCEF",   [10, 11, 12, 13, 14],         [20, 21, 22, 23, 24],
                    "ABCEFGH", [10, 11, 12, 13, 14, 15, 16], [20, 21, 22, 23, 24, XX, XX],
                    "ABCEFGH", [10, 11, 12, 13, 14, 15, 16], [20, 21, 22, 23, 24, XX, XX],
                ),
                (
                    # Trailing rows in B
                    "ABCEF", [10, 11, 12, 13, 14], 
                    "ABCEFGH", [20, 21, 22, 23, 24, 25, 26],
                    "ABCEF",   [10, 11, 12, 13, 14],         [20, 21, 22, 23, 24],
                    "ABCEFGH", [10, 11, 12, 13, 14, XX, XX], [20, 21, 22, 23, 24, 25, 26],
                    "ABCEF",   [10, 11, 12, 13, 14],         [20, 21, 22, 23, 24],
                ),
                (
                    # Leading rows in A
                    "ABCEF", [10, 11, 12, 13, 14], 
                    "CEF", [22, 23, 24],
                    "CEF",           [12, 13, 14],         [22, 23, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [XX, XX, 22, 23, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [XX, XX, 22, 23, 24],
                ),
                (
                    # Leading rows in B
                    "CEF", [12, 13, 14], 
                    "ABCEF", [20, 21, 22, 23, 24],
                    "CEF",           [12, 13, 14],         [22, 23, 24],
                    "ABCEF", [XX, XX, 12, 13, 14], [20, 21, 22, 23, 24],
                    "CEF",           [12, 13, 14],         [22, 23, 24],
                ),
                (
                    # Hole in A
                    "AF", [10, 14], 
                    "ABCEF", [20, 21, 22, 23, 24],
                    "AF",    [10,             14], [20,             24],
                    "ABCEF", [10, XX, XX, XX, 14], [20, 21, 22, 23, 24],
                    "AF",    [10,             14], [20,             24],
                ),
                (
                    # Hole in B
                    "ABCEF", [10, 11, 12, 13, 14], 
                    "AF", [20, 24],
                    "AF",    [10,             14], [20,             24],
                    "ABCEF", [10, 11, 12, 13, 14], [20, XX, XX, XX, 24],
                    "ABCEF", [10, 11, 12, 13, 14], [20, XX, XX, XX, 24],
                ),
                (
                    # Disjoint sets, A leading
                    "ABC", [10, 11, 12], 
                    "EFG", [23, 24, 25],
                    "",       [],                       [],
                    "ABCEFG", [10, 11, 12, XX, XX, XX], [XX, XX, XX, 23, 24, 25],
                    "ABC",    [10, 11, 12,],            [XX, XX, XX],
                ),
                (
                    # Disjoint sets, B leading
                    "EFG", [10, 11, 12], 
                    "ABC", [23, 24, 25],
                    "",       [],                       [],
                    "ABCEFG", [XX, XX, XX, 10, 11, 12], [23, 24, 25, XX, XX, XX],
                    "EFG",    [10, 11, 12],             [XX, XX, XX],
                ),
            )

        join_id, join_fct = join.value
        for indexA, colA, indexB, colB, *expected in testcases:
            expIndex, expLeft, expRight = expected[join_id*3:(join_id+1)*3]

            with self.subTest(fct=join_fct, indices=(indexA, indexB)):
                ser0 = serie.Serie.create(fc.sequence(indexA), fc.sequence(colA))
                ser1 = serie.Serie.create(fc.sequence(indexB), fc.sequence(colB))

                index, (left,), (right,) = join_fct(ser0, ser1)

                self.assertSequenceEqual(index.py_values, expIndex)

                self.assertSequenceEqual(left.py_values, expLeft)
                self.assertSequenceEqual(right.py_values, expRight)

    def test_serie_all_join(self):
        for join in TestJoin.Join:
            self.run_join_engine(join)

    def test_serie_inner_join_operator(self):
        serA = serie.Serie.create(fc.sequence("ABCDFG"), fc.sequence([10, 11, 12, 13, 14, 15]))
        serB = serie.Serie.create(fc.sequence("ABCEF"), fc.sequence([20, 21, 22, 23, 24]))

        join = serA & serB

        self.assertSequenceEqual(join.index.py_values, "ABCF")

        self.assertSequenceEqual(join.columns[0].py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(join.columns[1].py_values, [20, 21, 22, 24])

    def test_serie_full_outer_join_operator(self):
        XX=None
        serA = serie.Serie.create(fc.sequence("ABCDFG"), fc.sequence([10, 11, 12, 13, 14, 15]))
        serB = serie.Serie.create(fc.sequence("ABCEF"), fc.sequence([20, 21, 22, 23, 24]))

        join = serA | serB

        self.assertSequenceEqual(join.index.py_values, "ABCDEFG")

        self.assertSequenceEqual(join.columns[0].py_values, [10, 11, 12, 13, XX, 14, 15])
        self.assertSequenceEqual(join.columns[1].py_values, [20, 21, 22, XX, 23, 24, XX])

# ======================================================================
# Extra factory methods
# ======================================================================
class TestSerieFromData(unittest.TestCase):
    def test_from_data(self):
        columns = (
                # col A
                tuple(range(5)),
                # col B
                tuple(range(10,15)),
                # col C
                tuple(range(20,25)),
        )
        headings = "ABC"

        ser = serie.Serie.from_data(columns, headings)

        self.assertEqual(len(ser.columns), 2)
        self.assertEqual(ser.rowcount, 5)

        self.assertEqual(ser.index.name, "A")
        self.assertSequenceEqual(ser.index.py_values, range(0,5))
        self.assertEqual(ser.columns[0].name, "B")
        self.assertSequenceEqual(ser.columns[0].py_values, range(10,15))
        self.assertEqual(ser.columns[1].name, "C")
        self.assertSequenceEqual(ser.columns[1].py_values, range(20,25))


class TestSerieFromCSV(unittest.TestCase):
    def test_from_csv_numbers_only(self):
        from textwrap import dedent
        text = dedent("""\
            A, B, C
            0,10,20
            1,11,21
            2,12,22
            3,13,23
            4,14,24
        """)
        ser = serie.Serie.from_csv(
                iter(text.splitlines()),
                format='nnn'
        )

        self.assertEqual(len(ser.columns), 2)
        self.assertEqual(ser.rowcount, 5)

        self.assertEqual(ser.index.name, "A")
        self.assertSequenceEqual(ser.index.py_values, range(0,5))
        self.assertEqual(ser.columns[0].name, "B")
        self.assertSequenceEqual(ser.columns[0].py_values, range(10,15))
        self.assertEqual(ser.columns[1].name, "C")
        self.assertSequenceEqual(ser.columns[1].py_values, range(20,25))

    def test_from_csv_file(self):
        ser = serie.Serie.from_csv_file(
                "tests/_fixtures/MCD-20200103-20230103.csv",
                format="dnnnnni"
                )
        self.assertIsInstance(ser, serie.Serie)
        self.assertEqual(ser.rowcount, 756)


# ======================================================================
# Projections
# ======================================================================
class TestSerieStrip(unittest.TestCase):
    def setUp(self):
        XX=None
        self.cols = tuple(zip(*(
            (11,XX,XX,XX,XX,),
            (12,XX,32,XX,52,),
            (13,XX,33,43,53,),
            (14,24,XX,44,54,),
            (15,25,35,45,55,),
            (16,XX,36,46,56,),
            (17,27,37,47,57,),
            (18,28,38,48,58,),
            (19,29,39,49,59,),
        )))

        self.ser = serie.Serie.from_data(self.cols, "ABCDE")

    def test_lstrip(self):
        cols, ser = self.cols, self.ser
        res = ser.lstrip()

        self.assertEqual(res.rowcount, ser.rowcount-1)
        self.assertEqual(len(res.columns), 4)
        self.assertSequenceEqual(res.index.py_values, cols[0][1:])
        self.assertSequenceEqual(res.columns[0].py_values, cols[1][1:])

    def test_lstrip_select(self):
        cols, ser = self.cols, self.ser
        res = ser.lstrip("B")

        self.assertEqual(res.rowcount, ser.rowcount-3)
        self.assertEqual(len(res.columns), 4)
        self.assertSequenceEqual(res.index.py_values, cols[0][3:])
        self.assertSequenceEqual(res.columns[0].py_values, cols[1][3:])


class TestSerieSelect(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(zip(*(
            (11,21,31,41,51,),
            (12,22,32,42,52,),
            (13,23,33,43,53,),
            (14,24,34,44,54,),
            (15,25,35,45,55,),
            (16,26,36,46,56,),
            (17,27,37,47,57,),
            (18,28,38,48,58,),
            (19,29,39,49,59,),
        )))

        self.serie = serie.Serie.from_data(self.cols, "ABCDE")

    def test_select_single(self):
        a = self.serie
        cols = self.cols

        b = a.select(
                "B",
                )

        self.assertEqual(b.rowcount, a.rowcount)
        self.assertSequenceEqual(b.index.py_values, cols[1])
        self.assertEqual(len(b.columns), 0)

    def test_select_multi(self):
        a = self.serie
        cols = self.cols

        b = a.select(
                "A",
                (fc.add, "B", "C"),
                fc.constant(42),
                )

        self.assertEqual(b.rowcount, a.rowcount)
        self.assertSequenceEqual(b.index, a.index)
        self.assertEqual(len(b.columns), 2)
        self.assertSequenceEqual(b.index.py_values, cols[0])
        self.assertSequenceEqual(b.columns[0].py_values, [x+y for x,y in zip(cols[1], cols[2])])
        self.assertSequenceEqual(b.columns[1].py_values, (42,)*a.rowcount)


class TestSerieExtend(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(zip(*(
            (11,21,31,41,51,),
            (12,22,32,42,52,),
            (13,23,33,43,53,),
            (14,24,34,44,54,),
            (15,25,35,45,55,),
            (16,26,36,46,56,),
            (17,27,37,47,57,),
            (18,28,38,48,58,),
            (19,29,39,49,59,),
        )))

        self.serie = serie.Serie.from_data(self.cols, "ABCDE")

    def test_extend(self):
        a = self.serie
        cols = self.cols

        b = a.extend(
                (fc.named("F"), fc.range(61,70)),
                )

        self.assertEqual(b.rowcount, a.rowcount)
        self.assertEqual(len(b.columns), len(a.columns)+1)
        self.assertSequenceEqual(b.columns[-1].py_values, range(61, 70))


class TestSerieWhere(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(zip(*(
            (11,29,30,49,51,),
            (12,28,30,48,52,),
            (13,27,39,43,53,),
            (14,26,39,42,54,),
            (15,25,30,47,55,),
            (16,24,30,46,56,),
            (17,23,30,45,57,),
            (18,22,39,41,58,),
            (19,21,30,44,59,),
        )))

        self.serie = serie.Serie.from_data(self.cols, "ABCDE")

    def test_where(self):
        FA = False
        TR = True
        usecases = (
                # :bomb: Zero-length index are not supported !
#                "NULL serie",
#                (
#                    #  0   1   2   3   4   5   6   7   8
#                    ( FA, FA, FA, FA, FA, FA, FA, FA, FA ),
#                ),
#                (),
                "All, one expr",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR ),
                ),
                (      0,  1,  2,  3,  4,  5,  6,  7,  8 ),
                "All, two expr",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR, ),
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR, ),
                ),
                (      0,  1,  2,  3,  4,  5,  6,  7,  8, ),
                "First, two expr",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR, ),
                    ( TR, FA, FA, FA, FA, FA, FA, FA, FA, ),
                ),
                (      0,                                ),
                "Last, two expr",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR, ),
                    ( FA, FA, FA, FA, FA, FA, FA, FA, TR, ),
                ),
                (                                      8, ),
                "First and last, two expr (case 1)",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, TR, TR, TR, TR, TR, ),
                    ( TR, FA, FA, FA, FA, FA, FA, FA, TR, ),
                ),
                (      0,                              8, ),
                "First and last, two expr (case 2)",
                (
                    #  0   1   2   3   4   5   6   7   8
                    ( TR, TR, TR, TR, FA, FA, FA, FA, TR, ),
                    ( TR, FA, FA, FA, FA, TR, TR, TR, TR, ),
                ),
                (      0,                              8, ),
            )

        while usecases:
            desc, exprs, expected, *usecases = usecases

            with self.subTest(desc=desc):
                a = self.serie
                b = a.where(*(column.Column.from_sequence(expr) for expr in exprs))

                self.assertIsInstance(b, serie.Serie)
                self.assertSequenceEqual(b.headings, a.headings)
                self.assertSequenceEqual(b.index.py_values, [a.index[n] for n in expected])
                self.assertSequenceEqual(b.columns[0].py_values, [a.columns[0][n] for n in expected])


class TestSerieGroupBy(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(zip(*(
            (11,99,10,41,51,),
            (12,99,10,42,52,),
            (13,99,00,43,53,),
            (14,00,00,44,54,),
            (15,99,00,45,55,),
            (16,99,10,46,56,),
            (17,00,10,47,57,),
            (18,00,00,48,58,),
            (19,00,00,49,59,),
        )))

        self.serie = serie.Serie.from_data(self.cols, "ABCDE")

    def test_get_strips(self):
        serie = self.serie.select("A", "B")
        strips = serie.get_strips()

        self.assertSequenceEqual(strips[:4], (3, 4, 6, 9))

    def test_group_by_column_name(self):
        a = self.serie
        cols = self.cols
        b = a.group_by(
                "B",
                (ag.first, "A"),
                (ag.first, "C"),
                )

        self.assertEqual(b.rowcount, 4)
        self.assertEqual(b.columns[0].name, "C")

    def test_group_by_rename(self):
        a = self.serie
        cols = self.cols
        b = a.group_by(
                "B",
                (ag.first, "A"),
                (ag.first, fc.named("D"), "C"),
                )

        self.assertEqual(b.rowcount, 4)
        self.assertEqual(b.columns[0].name, "D")

    def test_group_by_expr(self):
        a = self.serie
        cols = self.cols
        b = a.group_by(
                (fc.add, "B", "C"),
                (ag.first, "A"),
                (ag.first, "C"),
                )
        self.assertEqual(b.rowcount, 7)
        self.assertEqual(len(b.columns), 1)

class TestSerieSortBy(unittest.TestCase):
    def setUp(self):
        self.cols = tuple(zip(*(
            (11,29,30,49,51,),
            (12,28,30,48,52,),
            (13,27,39,43,53,),
            (14,26,39,42,54,),
            (15,25,30,47,55,),
            (16,24,30,46,56,),
            (17,23,30,45,57,),
            (18,22,39,41,58,),
            (19,21,30,44,59,),
        )))

        self.serie = serie.Serie.from_data(self.cols, "ABCDE")

    def test_sort_identity(self):
        a = self.serie
        b = a.sort_by("A")

        self.assertEqual(b, a)

    def test_sort_by(self):
        a = self.serie
        b = a.sort_by("B")

        self.assertSequenceEqual(b.headings, "BACDE")
        self.assertSequenceEqual(b.index.py_values, range(21,30))

class TestSerieUnion(unittest.TestCase):
    def test_union(self):
        serA = serie.Serie.create(
                (fc.named("T"), fc.sequence("ABC")),
                (fc.named("X"), fc.constant(0)),
            )
        serB = serie.Serie.create(
                (fc.named("T"), fc.sequence("DEF")),
                (fc.named("X"), fc.constant(1)),
            )

        res = serA.union(serB)

        self.assertSequenceEqual(res.index.py_values, "ABCDEF")
        self.assertSequenceEqual(res.columns[0].py_values, (0,0,0,1,1,1))


# ======================================================================
# Output
# ======================================================================
class TestSerieToOtherFormatsConversion(unittest.TestCase):
    def test_str_representation_1_column(self):
        ser = serie.Serie.create(
                (fc.named("T"), fc.sequence("ABCDF")),
                (fc.named("V"), fc.sequence([10, 20, 30, 40, 50])),
        )
        expected="\n".join((
            "T | V ",
            "- | --",
            "A | 10",
            "B | 20",
            "C | 30",
            "D | 40",
            "F | 50",
        ))

        self.assertEqual(str(ser), expected)

    def test_str_representation_2_columns(self):
        ser = serie.Serie.create(
                (fc.named("T"), fc.sequence("ABC")), 
                (fc.named("V"), fc.sequence([10, 20, 30]))
        ) & serie.Serie.create(
                (fc.named("T"), fc.sequence("ABC")), 
                (fc.named("W"), fc.sequence([11, 21, 31]))
        )

        expected = "\n".join((
            "T | V  | W ",
            "- | -- | --",
            "A | 10 | 11",
            "B | 20 | 21",
            "C | 30 | 31",
        ))

        self.assertEqual(str(ser), expected)

# ======================================================================
# Column expressions evaluation
# ======================================================================


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def arithmetic_test(validator, fct):
    def _arithmetic_test(self):
        x = 1.5
        y = 2.0
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.constant(x)),
                (fct, "X", fc.constant(y)),
                )

        self.assertEqual(len(ser.columns), 2)
        self.assertSequenceEqual(ser.columns[0].py_values,(x,)*6)
        self.assertSequenceEqual(ser.columns[1].py_values,(validator(x,y),)*6)

    return _arithmetic_test

# ----------------------------------------------------------------------
# Test class
# ----------------------------------------------------------------------
class TestSerieEvaluationExpression(unittest.TestCase):
    def test_name_single_column(self):
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.constant(1)),
                )

        self.assertEqual(len(ser.columns), 1)
        self.assertSequenceEqual(ser.columns[0].py_values,(1,)*6)
        self.assertEqual(ser.columns[0].name, "X")

    def test_references(self):
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.constant(1)),
                "X",
                )

        self.assertEqual(len(ser.columns), 2)
        self.assertSequenceEqual(ser.columns[0].py_values,(1,)*6)
        self.assertSequenceEqual(ser.columns[1].py_values,(1,)*6)
        self.assertEqual(ser.columns[0].name, "X")
        self.assertEqual(ser.columns[1].name, "X")

    def test_named_references(self):
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.constant(1)),
                (fc.named("Y"), "X"),
                )

        self.assertEqual(len(ser.columns), 2)
        self.assertSequenceEqual(ser.columns[0].py_values,(1,)*6)
        self.assertSequenceEqual(ser.columns[1].py_values,(1,)*6)
        self.assertEqual(ser.columns[0].name, "X")
        self.assertEqual(ser.columns[1].name, "Y")

    test_add = arithmetic_test(lambda x, y: x+y, fc.add)
    test_sub = arithmetic_test(lambda x, y: x-y, fc.sub)
    test_mul = arithmetic_test(lambda x, y: x*y, fc.mul)
    test_div = arithmetic_test(lambda x, y: x/y, fc.div)

    def test_trivial_left_outer_join(self):
        seqA = tuple(range(10,16))
        seqB = tuple(range(20,26))
        serA = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.sequence(seqA)),
                )

        serB = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("Y"), fc.sequence(seqB)),
                serA["X"],
                )


        self.assertEqual(len(serB.columns), 2)
        self.assertSequenceEqual(serB.columns[0].py_values,seqB)
        self.assertSequenceEqual(serB.columns[1].py_values,seqA)
        self.assertEqual(serB.columns[0].name, "Y")
        self.assertEqual(serB.columns[1].name, "X")

    def test_trivial_get(self):
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                (fc.named("X"), fc.constant(2)),
                (fc.named("Y"), fc.get("X")),
                )

        self.assertEqual(len(ser.columns), 2)
        self.assertSequenceEqual(ser.columns[0].py_values,(2,)*6)
        self.assertSequenceEqual(ser.columns[1].py_values,(2,)*6)
        self.assertEqual(ser.columns[0].name, "X")
        self.assertEqual(ser.columns[1].name, "Y")
