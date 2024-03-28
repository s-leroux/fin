import unittest

from fin.seq2 import serie
from fin.seq2 import column
from fin.seq2 import fc

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
class TestLeftJoin(unittest.TestCase):
    def test_serie_trivial_join(self):
        seqA = [10, 11, 12, 13, 14, 15]
        seqB = [20, 21, 22, 23, 24, 25]
        serA = serie.Serie.create(fc.sequence("ABCD"), fc.sequence(seqA))
        serB = serie.Serie.create(fc.sequence("ABCD"), fc.sequence(seqB))

        index, (left,), (right,) = serie.left_join(serA, serB)

        self.assertSequenceEqual(index, serA.index)
        self.assertSequenceEqual(index, serB.index) # <- this is implicitly true


        self.assertSequenceEqual(left.py_values, seqA)
        self.assertSequenceEqual(right.py_values, seqB)

class TestInnerJoin(unittest.TestCase):
    def test_serie_join(self):
        ser0 = serie.Serie.create(fc.sequence("ABCDFG"), fc.sequence([10, 11, 12, 13, 14, 15]))
        ser1 = serie.Serie.create(fc.sequence("ABCEF"), fc.sequence([20, 21, 22, 23, 24]))

        index, (left,), (right,) = serie.join(ser0, ser1)

        self.assertSequenceEqual(index.py_values, "ABCF")

        self.assertSequenceEqual(left.py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(right.py_values, [20, 21, 22, 24])

    def test_serie_join_operator(self):
        serA = serie.Serie.create(fc.sequence("ABCDFG"), fc.sequence([10, 11, 12, 13, 14, 15]))
        serB = serie.Serie.create(fc.sequence("ABCEF"), fc.sequence([20, 21, 22, 23, 24]))

        join = serA & serB

        self.assertSequenceEqual(join.index.py_values, "ABCF")

        self.assertSequenceEqual(join.columns[0].py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(join.columns[1].py_values, [20, 21, 22, 24])

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
        self.assertEqual(res.index.py_values, cols[0][1:])
        self.assertEqual(res.columns[0].py_values, cols[1][1:])

    def test_lstrip_select(self):
        cols, ser = self.cols, self.ser
        res = ser.lstrip("B")

        self.assertEqual(res.rowcount, ser.rowcount-3)
        self.assertEqual(len(res.columns), 4)
        self.assertEqual(res.index.py_values, cols[0][3:])
        self.assertEqual(res.columns[0].py_values, cols[1][3:])



class TestSerieSelect(unittest.TestCase):
    def test_select(self):
        cols = tuple(zip(*(
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

        a = serie.Serie.from_data(cols, "ABCDE")
        b = a.select(
                "A",
                (fc.add, "B", "C"),
                fc.constant(42),
                )

        self.assertEqual(b.rowcount, a.rowcount)
        self.assertSequenceEqual(b.index, a.index)
        self.assertEqual(len(b.columns), 3)
        self.assertSequenceEqual(b.columns[0].py_values, cols[0])
        self.assertSequenceEqual(b.columns[1].py_values, [x+y for x,y in zip(cols[1], cols[2])])
        self.assertSequenceEqual(b.columns[2].py_values, (42,)*a.rowcount)
        


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
            "T, V",
            "A, 10",
            "B, 20",
            "C, 30",
            "D, 40",
            "F, 50",
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

        expected="\n".join((
            "T, V, W",
            "A, 10, 11",
            "B, 20, 21",
            "C, 30, 31",
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

    def test_trivial_left_join(self):
        seqA = tuple(range(10,17))
        seqB = tuple(range(20,27))
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

    def test_all(self):
        ser = serie.Serie.create(
                fc.sequence("ABCDEF"),
                fc.constant(2),
                fc.constant(3),
                fc.constant(4),
                )

        cols = ser.evaluate(fc.all)
        self.assertSequenceEqual(cols, ser.columns)

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
