import unittest

from fin.seq2 import serie
from fin.seq2 import column

class TestSerie(unittest.TestCase):
    def test_create_serie_from_lists(self):
        """
        You can create a serie from lists.
        """
        ser = serie.Serie("ABC", [10, 20, 30])

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
        serA = serie.Serie("ABCDF", seqA)
        scalar = 3

        serB = serA + scalar
        self.assertSequenceEqual(serB.index.py_values, "ABCDF")
        self.assertEqual(len(serB.columns), 1)
        self.assertSequenceEqual(serB.columns[0].f_values, [x+scalar for x in seqA])

    def test_add_series(self):
        """
        Adding two sequences performs an implicit join.
        """
        serA = serie.Serie("ABCDF", [10, 20, 30, 40, 50])
        serB = serie.Serie("ABCEF", [11, 21, 31, 41, 51])

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

        ser = serie.Serie(*cols)

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

        ser = serie.Serie(*cols)
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

        ser = serie.Serie(*cols)

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

        ser = serie.Serie(*cols)
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

        ser = serie.Serie(*cols)
        res = ser.clear()

        self.assertIsInstance(res, serie.Serie)
        self.assertEqual(res.index, c1)
        self.assertEqual(len(res.columns), 0)

class TestJoin(unittest.TestCase):
    def test_serie_join(self):
        ser0 = serie.Serie("ABCDFG", [10, 11, 12, 13, 14, 15])
        ser1 = serie.Serie("ABCEF", [20, 21, 22, 23, 24])

        index, (left,), (right,) = serie.join(ser0, ser1)

        self.assertSequenceEqual(index.py_values, "ABCF")

        self.assertSequenceEqual(left.py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(right.py_values, [20, 21, 22, 24])

    def test_serie_join_operator(self):
        serA = serie.Serie("ABCDFG", [10, 11, 12, 13, 14, 15])
        serB = serie.Serie("ABCEF", [20, 21, 22, 23, 24])

        join = serA & serB

        self.assertSequenceEqual(join.index.py_values, "ABCF")

        self.assertSequenceEqual(join.columns[0].py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(join.columns[1].py_values, [20, 21, 22, 24])

class TestSerieToOtherFormatsConversion(unittest.TestCase):
    def test_str_representation_1_column(self):
        ser = serie.Serie("ABCDF", [10, 20, 30, 40, 50])
        expected="\n".join((
            "A, 10",
            "B, 20",
            "C, 30",
            "D, 40",
            "F, 50",
        ))

        self.assertEqual(str(ser), expected)

    def test_str_representation_2_columns(self):
        ser = serie.Serie("ABC", [10, 20, 30]) & serie.Serie("ABC", [11, 21, 31])
        expected="\n".join((
            "A, 10, 11",
            "B, 20, 21",
            "C, 30, 31",
        ))

        self.assertEqual(str(ser), expected)

